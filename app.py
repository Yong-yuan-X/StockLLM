import logging
import os
import secrets
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, g, make_response, render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename

from core.config import DATABASE, FORUM_UPLOAD_DIR, USER_AVATAR_DIR, ensure_runtime_directories
from core.db import get_db, init_db
from core.network import configure_requests
from core.services.analysis_service import (
    DEFAULT_CASE_ORDER,
    build_stock_chart_payload,
    predict_market_index_movement,
    predict_stock_movement,
    update_stock_history_csv,
)
from core.services.api_response import error_response, success_response
from core.services.email_service import send_html_email
from core.services.llm_report_service import (
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_PROMPT,
    build_demo_report_context,
    build_stock_report_context,
)
from core.services.market_service import (
    fetch_favorite_snapshot,
    fetch_market_change_distribution,
    fetch_stock_rankings,
    fetch_sector_constituents,
    fetch_sector_options,
    fetch_stock_directory,
)
from core.services.report_service import render_report_html
from core.services.user_stock_service import (
    add_user_stock,
    approve_user_registration,
    create_test_user,
    delete_user_account,
    delete_user_stock,
    get_user_email,
    get_user_llm_prompts,
    get_user_profile,
    get_user_report_schedule_settings,
    is_valid_email,
    list_all_users,
    list_due_report_schedule_users,
    get_report_history,
    list_report_histories,
    login_user,
    mark_user_report_schedule_sent,
    list_user_stocks,
    register_user,
    save_user_email,
    save_email_verification_code,
    save_generated_report,
    save_user_profile,
    save_user_report_schedule_settings,
    save_user_llm_prompts,
    reset_user_password_by_email,
    verify_email_code,
)
from data_sources.market_index import get_market_index_data
from sentiment.services.sentiment_service import (
    fetch_market_sentiment,
    fetch_multi_stock_sentiment,
    fetch_sector_sentiment,
    fetch_stock_sentiment,
)


configure_requests()
ensure_runtime_directories()

app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")
flask_secret_key = os.environ.get("FLASK_SECRET_KEY", "").strip()
if len(flask_secret_key) < 32:
    raise RuntimeError("FLASK_SECRET_KEY 必须配置为至少 32 个字符的随机字符串")
app.config.update(
    DATABASE=DATABASE,
    SECRET_KEY=flask_secret_key,
    MAX_CONTENT_LENGTH=int(os.environ.get("MAX_UPLOAD_SIZE_MB", "10")) * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "false").strip().lower()
    in {"1", "true", "yes", "on"},
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
)
init_db(app)
APP_ROOT = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)
_schedule_thread = None
_schedule_thread_lock = threading.Lock()
_schedule_stop_event = threading.Event()


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    return response


def _load_session_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    row = get_db().execute(
        "SELECT id, uuid, username, email, avatar_path, avatar_name, is_admin, approval_status "
        "FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if not row or (not row["is_admin"] and (row["approval_status"] or "approved") != "approved"):
        session.clear()
        return None
    return row


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = _load_session_user()
        if not user:
            return error_response("请先登录", status=401)
        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = _load_session_user()
        if not user:
            return error_response("请先登录", status=401)
        if not user["is_admin"]:
            return error_response("仅管理员可执行此操作", status=403)
        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def _current_user_id():
    return int(g.current_user["id"])


def _optional_current_user_id():
    user = _load_session_user()
    return int(user["id"]) if user else None


def _validated_image_suffix(file_storage):
    original_name = secure_filename(file_storage.filename or "")
    suffix = Path(original_name).suffix.lower()
    if suffix == ".jpeg":
        suffix = ".jpg"
    if suffix not in {".png", ".jpg", ".gif", ".webp"}:
        raise ValueError("仅支持 png/jpg/jpeg/gif/webp 图片")

    header = file_storage.stream.read(16)
    file_storage.stream.seek(0)
    detected = None
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        detected = ".png"
    elif header.startswith(b"\xff\xd8\xff"):
        detected = ".jpg"
    elif header.startswith((b"GIF87a", b"GIF89a")):
        detected = ".gif"
    elif len(header) >= 12 and header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        detected = ".webp"
    if detected != suffix:
        raise ValueError("上传内容不是有效的图片文件")
    return suffix, original_name


def _build_scheduled_report_payload(user_id, stock_code):
    update_stock_history_csv(stock_code)
    analysis_data = predict_stock_movement(
        stock_code,
        7,
        selected_cases=DEFAULT_CASE_ORDER,
        risk_preference="balanced",
    )
    report_context = build_stock_report_context(stock_code, analysis_data, user_id=user_id)
    report_html = render_report_html(report_context)
    stock_name = report_context.get("stock_profile", {}).get("stock_name") or stock_code
    report_title = f"{stock_name} 7天定时分析报告"
    save_generated_report(
        user_id=user_id,
        stock_code=stock_code,
        stock_name=stock_name,
        report_title=report_title,
        report_html=report_html,
        report_context=report_context,
        report_payload=analysis_data,
    )
    return {"report_title": report_title, "report_html": report_html}


def _send_scheduled_reports_for_user(user_schedule):
    user_id = int(user_schedule["id"])
    email = str(user_schedule.get("email") or "").strip()
    stock_codes = [str(code or "").strip() for code in user_schedule.get("stock_codes") or [] if str(code or "").strip()]
    if not email or not stock_codes:
        return

    for stock_code in stock_codes:
        payload = _build_scheduled_report_payload(user_id, stock_code)
        send_html_email(email, payload["report_title"], payload["report_html"])


def _run_report_schedule_loop(flask_app):
    while not _schedule_stop_event.is_set():
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")
        try:
            with flask_app.app_context():
                due_users = list_due_report_schedule_users(current_time, current_date)
                for item in due_users:
                    try:
                        _send_scheduled_reports_for_user(item)
                        mark_user_report_schedule_sent(item["id"], now.strftime("%Y-%m-%d %H:%M:%S"))
                        logger.info("定时报告发送成功 user_id=%s time=%s", item["id"], current_time)
                    except Exception as exc:
                        logger.exception("定时报告发送失败 user_id=%s error=%s", item["id"], exc)
        except Exception as exc:
            logger.exception("定时报告调度循环异常: %s", exc)
        _schedule_stop_event.wait(20)


def start_report_scheduler():
    global _schedule_thread
    with _schedule_thread_lock:
        if _schedule_thread and _schedule_thread.is_alive():
            return
        _schedule_stop_event.clear()
        _schedule_thread = threading.Thread(
            target=_run_report_schedule_loop,
            args=(app,),
            name="report-scheduler",
            daemon=True,
        )
        _schedule_thread.start()
        logger.info("定时报告调度线程已启动")


@app.route("/")
def index():
    return render_template("webmange.html")


@app.route("/healthz")
def healthz():
    return {"status": "ok"}


@app.route("/gushi.jpg")
def auth_background_image():
    return send_from_directory(APP_ROOT, "gushi.jpg")


@app.route("/forum_uploads/<path:filename>")
def forum_upload_file(filename):
    direct_path = FORUM_UPLOAD_DIR / filename
    if direct_path.exists():
        return send_from_directory(FORUM_UPLOAD_DIR, filename)

    db = get_db()
    row = db.execute(
        "SELECT image_path FROM forum_posts WHERE image_name = ? OR image_path = ? ORDER BY id DESC LIMIT 1",
        (filename, filename),
    ).fetchone()
    if row and row["image_path"] and (FORUM_UPLOAD_DIR / row["image_path"]).exists():
        return send_from_directory(FORUM_UPLOAD_DIR, row["image_path"])
    return send_from_directory(FORUM_UPLOAD_DIR, filename)


@app.route("/user_avatars/<path:filename>")
def user_avatar_file(filename):
    return send_from_directory(USER_AVATAR_DIR, filename)


def _forum_image_url(image_path):
    return f"/forum_uploads/{image_path}" if image_path else ""


def _user_avatar_url(avatar_path):
    return f"/user_avatars/{avatar_path}" if avatar_path else ""


def _user_payload_with_avatar(user):
    return {**user, "avatar_url": _user_avatar_url(user.get("avatar_path"))} if user else user


@app.route("/report-preview")
def report_preview():
    return render_template("stock_report_preview.html", report=build_demo_report_context())


@app.route("/api/update_stock_data", methods=["POST"])
@login_required
def update_stock_data():
    try:
        payload = request.get_json(silent=True) or {}
        stock_code = payload.get("stock_code", "").strip()
        if not stock_code:
            return error_response("请输入股票代码！", status=400)
        data = update_stock_history_csv(stock_code)
        return success_response("数据更新成功！", data=data)
    except Exception as exc:
        return error_response(f"数据更新失败：{exc}", status=500)


@app.route("/api/market_indices", methods=["GET"])
def market_indices():
    try:
        days = request.args.get("days", default=90, type=int)
        k_type = request.args.get("k_type", default="day", type=str)
        return success_response("大盘指数获取成功", data=get_market_index_data(days=days, k_type=k_type))
    except Exception as exc:
        return error_response(f"大盘指数获取失败：{exc}", status=500)


@app.route("/api/sector_options", methods=["GET"])
def sector_options():
    try:
        return success_response("板块列表获取成功", data=fetch_sector_options())
    except Exception as exc:
        return error_response(f"板块列表获取失败：{exc}", status=500)


@app.route("/api/sector_stocks", methods=["GET"])
def sector_stocks():
    try:
        sector_data = fetch_sector_constituents(
            sector_name=request.args.get("sector_name", "").strip(),
            sector_code=request.args.get("sector_code", "").strip(),
            keyword=request.args.get("keyword", "").strip(),
            page=request.args.get("page", default=1, type=int),
            page_size=request.args.get("page_size", default=10, type=int),
        )
        return success_response("板块成分股获取成功", data=sector_data)
    except Exception as exc:
        return error_response(f"板块成分股获取失败：{exc}", status=500)


@app.route("/api/stock_directory", methods=["GET"])
def stock_directory():
    try:
        stock_data = fetch_stock_directory(
            keyword=request.args.get("keyword", "").strip(),
            page=request.args.get("page", default=1, type=int),
            page_size=request.args.get("page_size", default=20, type=int),
        )
        return success_response("个股明细获取成功", data=stock_data)
    except Exception as exc:
        return error_response(f"个股明细获取失败：{exc}", status=500)


@app.route("/api/stock_charts", methods=["GET"])
def stock_charts():
    try:
        stock_code = request.args.get("stock_code", "").strip()
        stock_name = request.args.get("stock_name", "").strip()
        days = request.args.get("days", default=90, type=int)
        if not stock_code:
            return error_response("请输入股票代码！", status=400)
        return success_response("个股图表数据获取成功", data=build_stock_chart_payload(stock_code, stock_name=stock_name, days=days))
    except FileNotFoundError as exc:
        return error_response(str(exc), status=404)
    except Exception as exc:
        return error_response(f"个股图表数据获取失败：{exc}", status=500)


@app.route("/api/stock_rankings", methods=["GET"])
def stock_rankings():
    try:
        limit = request.args.get("limit", default=10, type=int)
        return success_response("涨跌排行榜获取成功", data=fetch_stock_rankings(limit=limit))
    except Exception as exc:
        return error_response(f"涨跌排行榜获取失败：{exc}", status=500)


@app.route("/api/favorites_snapshot", methods=["GET"])
@login_required
def favorites_snapshot():
    try:
        return success_response("自选股快照获取成功", data=fetch_favorite_snapshot(_current_user_id()))
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"自选股快照获取失败：{exc}", status=500)


@app.route("/api/market_distribution", methods=["GET"])
def market_distribution():
    try:
        return success_response("全市场涨跌分布获取成功", data=fetch_market_change_distribution())
    except Exception as exc:
        return error_response(f"全市场涨跌分布获取失败：{exc}", status=500)


@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        payload = request.get_json(silent=True) or {}
        verify_email_code(payload.get("email"), payload.get("email_code"), purpose="register")
        user = register_user(payload.get("username"), payload.get("password"), payload.get("email"))
        verify_email_code(payload.get("email"), payload.get("email_code"), purpose="register", mark_used=True)
        return success_response("注册申请已提交，请等待管理员审核后登录", data={"user": _user_payload_with_avatar(user)})
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"注册失败：{exc}", status=500)


@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        payload = request.get_json(silent=True) or {}
        user = login_user(payload.get("username"), payload.get("password"))
        session.clear()
        session["user_id"] = int(user["id"])
        session.permanent = True
        return success_response("登录成功", data={"user": _user_payload_with_avatar(user)})
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"登录失败：{exc}", status=500)


@app.route("/api/auth/me", methods=["GET"])
@login_required
def current_user():
    return success_response(
        "查询成功",
        data={"user": _user_payload_with_avatar(dict(g.current_user))},
    )


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return success_response("已退出登录")


@app.route("/api/auth/reset_password", methods=["POST"])
def reset_password():
    try:
        payload = request.get_json(silent=True) or {}
        email = payload.get("email")
        email_code = payload.get("email_code")
        password = payload.get("password")
        account_identity = payload.get("username")
        verify_email_code(email, email_code, purpose="password_reset")
        reset_user_password_by_email(email, password, account_identity=account_identity)
        verify_email_code(email, email_code, purpose="password_reset", mark_used=True)
        return success_response("密码重置成功，请使用新密码登录")
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"密码重置失败：{exc}", status=500)


@app.route("/api/auth/send_email_code", methods=["POST"])
def send_email_code():
    try:
        payload = request.get_json(silent=True) or {}
        email = str(payload.get("email", "") or "").strip()
        purpose = str(payload.get("purpose", "register") or "register").strip()
        purpose_labels = {
            "register": "注册验证",
            "password_reset": "密码找回",
        }
        if purpose not in purpose_labels:
            return error_response("验证码用途不正确", status=400)
        if not email:
            return error_response("请输入邮箱", status=400)
        if not is_valid_email(email):
            return error_response("邮箱格式不正确", status=400)
        if purpose == "register":
            existing = get_db().execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                return error_response("该邮箱已注册", status=400)
        if purpose == "password_reset":
            existing = get_db().execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if not existing:
                return error_response("该邮箱尚未注册", status=400)

        code = f"{secrets.randbelow(1_000_000):06d}"
        save_email_verification_code(email, code, purpose=purpose)
        send_html_email(
            email,
            "StockLLM 邮箱验证码",
            (
                "<div style='font-family:Arial,sans-serif;line-height:1.8;color:#1f2937;'>"
                "<h2 style='margin-bottom:12px;'>邮箱验证码</h2>"
                f"<p>你的本次验证码为：<strong style='font-size:24px;color:#2563eb;'>{code}</strong></p>"
                f"<p>验证码 10 分钟内有效，仅用于{purpose_labels[purpose]}，请勿泄露给他人。</p>"
                "</div>"
            ),
        )
        return success_response("验证码发送成功")
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"验证码发送失败：{exc}", status=500)


@app.route("/api/users", methods=["GET"])
@admin_required
def users():
    try:
        return success_response("查询成功", data={"items": list_all_users(_current_user_id())})
    except PermissionError as exc:
        return error_response(str(exc), status=403)
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"查询用户失败：{exc}", status=500)


@app.route("/api/users/<int:target_user_id>", methods=["DELETE"])
@admin_required
def delete_user(target_user_id):
    try:
        deleted = delete_user_account(_current_user_id(), target_user_id)
        return success_response("用户已注销", data=deleted)
    except PermissionError as exc:
        return error_response(str(exc), status=403)
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"注销用户失败：{exc}", status=500)


@app.route("/api/users/<int:target_user_id>/approve", methods=["POST"])
@admin_required
def approve_user(target_user_id):
    try:
        approved = approve_user_registration(_current_user_id(), target_user_id)
        return success_response("用户审核已通过", data=approved)
    except PermissionError as exc:
        return error_response(str(exc), status=403)
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"审核用户失败：{exc}", status=500)


@app.route("/api/report_histories", methods=["GET"])
@login_required
def report_histories():
    try:
        stock_code = request.args.get("stock_code", "").strip() or None
        return success_response(
            "查询成功",
            data={"items": list_report_histories(_current_user_id(), stock_code=stock_code)},
        )
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"历史报告获取失败：{exc}", status=500)


@app.route("/api/report_histories/<int:history_id>/download", methods=["GET"])
@login_required
def download_report_history(history_id):
    try:
        history = get_report_history(_current_user_id(), history_id)
        filename = f"{history['stock_code'] or 'report'}_{history['created_at'].replace(':', '-').replace(' ', '_')}.html"
        response = make_response(history.get("report_html") or "")
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except PermissionError as exc:
        return error_response(str(exc), status=403)
    except Exception as exc:
        return error_response(f"历史报告下载失败：{exc}", status=500)


@app.route("/api/predict_stock", methods=["POST"])
@login_required
def predict_stock():
    try:
        started_at = time.perf_counter()
        payload = request.get_json(silent=True) or {}
        stock_code = payload.get("stock_code", "").strip()
        days = int(payload.get("days", 0))
        selected_cases = payload.get("selected_cases") or []
        risk_preference = payload.get("risk_preference")
        user_id = _current_user_id()

        if not stock_code:
            return error_response("请输入股票代码！", status=400)

        timing_breakdown = {}

        update_started_at = time.perf_counter()
        update_summary = update_stock_history_csv(stock_code)
        timing_breakdown["update_stock_history_seconds"] = round(time.perf_counter() - update_started_at, 3)

        analysis_started_at = time.perf_counter()
        data = predict_stock_movement(stock_code, days, selected_cases=selected_cases, risk_preference=risk_preference)
        timing_breakdown["analysis_seconds"] = round(time.perf_counter() - analysis_started_at, 3)
        data["update_summary"] = update_summary

        report_context_started_at = time.perf_counter()
        report_context = build_stock_report_context(stock_code, data, user_id=user_id)
        timing_breakdown["build_report_context_seconds"] = round(time.perf_counter() - report_context_started_at, 3)
        data["report_context"] = report_context

        render_started_at = time.perf_counter()
        data["report_html"] = render_report_html(report_context)
        timing_breakdown["render_report_html_seconds"] = round(time.perf_counter() - render_started_at, 3)
        report_id = None
        if user_id:
            save_started_at = time.perf_counter()
            report_id = save_generated_report(
                user_id=user_id,
                stock_code=stock_code,
                stock_name=report_context.get("stock_profile", {}).get("stock_name") or stock_code,
                report_title=f"{stock_code} {days}天趋势分析报告",
                report_html=data["report_html"],
                report_context=report_context,
                report_payload=data,
            )
            timing_breakdown["save_generated_report_seconds"] = round(time.perf_counter() - save_started_at, 3)
        else:
            timing_breakdown["save_generated_report_seconds"] = 0.0
        data["report_id"] = report_id
        timing_breakdown["total_seconds"] = round(time.perf_counter() - started_at, 3)
        data["timing_breakdown"] = timing_breakdown
        logger.info(
            "生成分析报告耗时 stock=%s total=%.3fs update=%.3fs analysis=%.3fs report_context=%.3fs render_html=%.3fs save=%.3fs",
            stock_code,
            timing_breakdown["total_seconds"],
            timing_breakdown["update_stock_history_seconds"],
            timing_breakdown["analysis_seconds"],
            timing_breakdown["build_report_context_seconds"],
            timing_breakdown["render_report_html_seconds"],
            timing_breakdown["save_generated_report_seconds"],
        )
        return success_response("预测成功！", data=data)
    except ValueError as exc:
        return error_response(str(exc) + "！", status=400)
    except FileNotFoundError as exc:
        return error_response(str(exc), status=404)
    except Exception as exc:
        return error_response(f"预测失败：{exc}", status=500)


@app.route("/api/predict_market_index", methods=["POST"])
@login_required
def predict_market_index():
    try:
        started_at = time.perf_counter()
        payload = request.get_json(silent=True) or {}
        index_key = str(payload.get("index_key", "") or "").strip()
        days = int(payload.get("days", 0))
        selected_cases = payload.get("selected_cases") or []
        risk_preference = payload.get("risk_preference")
        user_id = _current_user_id()

        if not index_key:
            return error_response("请选择大盘指数", status=400)

        timing_breakdown = {}

        analysis_started_at = time.perf_counter()
        data = predict_market_index_movement(index_key, days, selected_cases=selected_cases, risk_preference=risk_preference)
        timing_breakdown["analysis_seconds"] = round(time.perf_counter() - analysis_started_at, 3)

        report_context_started_at = time.perf_counter()
        report_context = build_stock_report_context(index_key, data, user_id=user_id)
        timing_breakdown["build_report_context_seconds"] = round(time.perf_counter() - report_context_started_at, 3)
        data["report_context"] = report_context

        render_started_at = time.perf_counter()
        data["report_html"] = render_report_html(report_context)
        timing_breakdown["render_report_html_seconds"] = round(time.perf_counter() - render_started_at, 3)
        data["update_summary"] = {
            "stock_code": index_key,
            "date_range": f"{data['data_summary']['date_start']} 至 {data['data_summary']['date_end']}",
            "file_path": data.get("source_file"),
            "data_count": data["data_summary"]["rows"],
            "data_source_label": "大盘指数缓存",
        }
        report_id = None
        if user_id:
            save_started_at = time.perf_counter()
            report_id = save_generated_report(
                user_id=user_id,
                stock_code=index_key,
                stock_name=report_context.get("stock_profile", {}).get("stock_name") or index_key,
                report_title=f"{report_context.get('stock_profile', {}).get('stock_name') or index_key} {days}天趋势分析报告",
                report_html=data["report_html"],
                report_context=report_context,
                report_payload=data,
            )
            timing_breakdown["save_generated_report_seconds"] = round(time.perf_counter() - save_started_at, 3)
        else:
            timing_breakdown["save_generated_report_seconds"] = 0.0
        data["report_id"] = report_id
        timing_breakdown["total_seconds"] = round(time.perf_counter() - started_at, 3)
        data["timing_breakdown"] = timing_breakdown
        logger.info(
            "生成大盘分析报告耗时 index=%s total=%.3fs analysis=%.3fs report_context=%.3fs render_html=%.3fs save=%.3fs",
            index_key,
            timing_breakdown["total_seconds"],
            timing_breakdown["analysis_seconds"],
            timing_breakdown["build_report_context_seconds"],
            timing_breakdown["render_report_html_seconds"],
            timing_breakdown["save_generated_report_seconds"],
        )
        return success_response("大盘分析成功", data=data)
    except ValueError as exc:
        return error_response(str(exc) + "！", status=400)
    except FileNotFoundError as exc:
        return error_response(str(exc), status=404)
    except Exception as exc:
        return error_response(f"大盘分析失败：{exc}", status=500)


@app.route("/api/add_stock", methods=["POST"])
@login_required
def add_stock():
    try:
        payload = request.get_json(silent=True) or {}
        add_user_stock(
            user_id=_current_user_id(),
            stock_code=payload.get("stock_code"),
            stock_name=payload.get("stock_name"),
        )
        return success_response("添加成功")
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except sqlite3.IntegrityError as exc:
        return error_response(str(exc), status=409)
    except Exception as exc:
        return error_response(f"服务器错误：{exc}", status=500)


@app.route("/api/get_stocks", methods=["GET"])
@login_required
def get_stocks():
    try:
        return success_response("查询成功", data=list_user_stocks(_current_user_id()))
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"服务器错误：{exc}", status=500)


@app.route("/api/user_settings/email", methods=["GET"])
@login_required
def get_settings_email():
    try:
        return success_response("查询成功", data={"email": get_user_email(_current_user_id())})
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"服务器错误：{exc}", status=500)


@app.route("/api/user_settings/profile", methods=["GET"])
@login_required
def get_settings_profile():
    try:
        user = get_user_profile(_current_user_id())
        return success_response(
            "查询成功",
            data={
                "user": _user_payload_with_avatar(user)
            },
        )
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"服务器错误：{exc}", status=500)


@app.route("/api/user_settings/profile", methods=["POST"])
@login_required
def save_settings_profile():
    try:
        username = str(request.form.get("username", "") or "").strip()
        avatar_file = request.files.get("avatar")
        avatar_path = None
        avatar_name = None

        if avatar_file and avatar_file.filename:
            suffix, original_name = _validated_image_suffix(avatar_file)
            avatar_name = original_name
            avatar_path = f"{uuid.uuid4().hex}{suffix}"
            avatar_file.save(USER_AVATAR_DIR / avatar_path)

        user = save_user_profile(
            user_id=_current_user_id(),
            username=username,
            avatar_path=avatar_path,
            avatar_name=avatar_name,
        )
        return success_response(
            "用户资料保存成功",
            data={
                "user": _user_payload_with_avatar(user)
            },
        )
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"服务器错误：{exc}", status=500)


@app.route("/api/user_settings/email", methods=["POST"])
@login_required
def save_settings_email():
    try:
        payload = request.get_json(silent=True) or {}
        saved_email = save_user_email(
            user_id=_current_user_id(),
            email=payload.get("email"),
        )
        return success_response("邮箱保存成功", data={"email": saved_email})
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"服务器错误：{exc}", status=500)


@app.route("/api/user_settings/report_schedule", methods=["GET"])
@login_required
def get_settings_report_schedule():
    try:
        return success_response("查询成功", data=get_user_report_schedule_settings(_current_user_id()))
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"服务器错误：{exc}", status=500)


@app.route("/api/user_settings/report_schedule", methods=["POST"])
@login_required
def save_settings_report_schedule():
    try:
        payload = request.get_json(silent=True) or {}
        settings = save_user_report_schedule_settings(
            user_id=_current_user_id(),
            enabled=payload.get("enabled"),
            schedule_time=payload.get("time"),
            stock_codes=payload.get("stock_codes"),
        )
        return success_response("定时发送设置保存成功", data=settings)
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"服务器错误：{exc}", status=500)


@app.route("/api/send_report", methods=["POST"])
@login_required
def send_report():
    try:
        payload = request.get_json(silent=True) or {}
        stock_code = str(payload.get("stock_code", "") or "").strip()
        email = get_user_email(_current_user_id())
        if not email:
            return error_response("请先在设置中保存接收报告邮箱", status=400)

        subject = f"股票分析报告测试 - {stock_code}" if stock_code else "股票分析报告测试"
        html_body = render_report_html(payload.get("report_context"))
        send_html_email(email, subject, html_body)
        return success_response("报告发送成功", data={"email": email, "subject": subject})
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"报告发送失败：{exc}", status=500)


@app.route("/api/user_settings/llm_prompts", methods=["GET"])
@login_required
def get_settings_llm_prompts():
    try:
        prompts = get_user_llm_prompts(_current_user_id())
        return success_response(
            "查询成功",
            data={
                "system_prompt": prompts.get("system_prompt") or DEFAULT_SYSTEM_PROMPT,
                "user_prompt": prompts.get("user_prompt") or DEFAULT_USER_PROMPT,
            },
        )
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"服务器错误：{exc}", status=500)


@app.route("/api/user_settings/llm_prompts", methods=["POST"])
@login_required
def save_settings_llm_prompts():
    try:
        payload = request.get_json(silent=True) or {}
        saved_prompts = save_user_llm_prompts(
            user_id=_current_user_id(),
            system_prompt=payload.get("system_prompt"),
            user_prompt=payload.get("user_prompt"),
        )
        return success_response("Prompt 保存成功", data=saved_prompts)
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"服务器错误：{exc}", status=500)


@app.route("/api/sentiment/market", methods=["GET"])
def market_sentiment():
    try:
        days = request.args.get("days", default=2, type=int)
        start_time = request.args.get("start_time", "").strip() or None
        end_time = request.args.get("end_time", "").strip() or None
        stage = request.args.get("stage", default="full", type=str)
        return success_response("大盘舆情获取成功", data=fetch_market_sentiment(days=days, start_time=start_time, end_time=end_time, stage=stage))
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"大盘舆情获取失败：{exc}", status=500)


@app.route("/api/sentiment/sector", methods=["GET"])
def sector_sentiment():
    try:
        sector_name = request.args.get("sector_name", "").strip()
        days = request.args.get("days", default=2, type=int)
        start_time = request.args.get("start_time", "").strip() or None
        end_time = request.args.get("end_time", "").strip() or None
        stage = request.args.get("stage", default="full", type=str)
        return success_response("板块舆情获取成功", data=fetch_sector_sentiment(sector_name, days=days, start_time=start_time, end_time=end_time, stage=stage))
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"板块舆情获取失败：{exc}", status=500)


@app.route("/api/sentiment/stock", methods=["GET"])
def stock_sentiment():
    try:
        stock_code = request.args.get("stock_code", "").strip()
        days = request.args.get("days", default=2, type=int)
        debug = (
            request.args.get("debug", default=0, type=int) == 1
            and _env_flag("ENABLE_SENTIMENT_DEBUG", False)
        )
        start_time = request.args.get("start_time", "").strip() or None
        end_time = request.args.get("end_time", "").strip() or None
        stage = request.args.get("stage", default="full", type=str)
        if any(separator in stock_code for separator in [" ", ",", "，", "、", "\n", "\t", ";", "；", "|"]):
            return success_response("个股舆情获取成功", data=fetch_multi_stock_sentiment(stock_code, days=days, start_time=start_time, end_time=end_time, stage=stage))
        return success_response("个股舆情获取成功", data=fetch_stock_sentiment(stock_code, days=days, debug=debug, start_time=start_time, end_time=end_time, stage=stage))
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"个股舆情获取失败：{exc}", status=500)


@app.route("/api/forum/posts", methods=["GET"])
def list_forum_posts():
    try:
        limit = max(1, min(request.args.get("limit", default=50, type=int), 200))
        sort_by = (request.args.get("sort_by", default="created_at", type=str) or "created_at").strip().lower()
        user_id = _optional_current_user_id()
        db = get_db()
        order_clause = {
            "likes": "like_count DESC, comment_count DESC, forum_posts.created_at DESC, forum_posts.id DESC",
            "comments": "comment_count DESC, like_count DESC, forum_posts.created_at DESC, forum_posts.id DESC",
            "created_at": "forum_posts.created_at DESC, forum_posts.id DESC",
        }.get(sort_by, "forum_posts.created_at DESC, forum_posts.id DESC")
        rows = db.execute(
            f"""
            SELECT forum_posts.id, forum_posts.content, forum_posts.image_path, forum_posts.image_name,
                   forum_posts.created_at, forum_posts.user_id,
                   users.username, users.uuid, users.avatar_path,
                   COUNT(DISTINCT forum_comments.id) AS comment_count,
                   COUNT(DISTINCT forum_post_likes.id) AS like_count,
                   MAX(CASE WHEN forum_post_likes.user_id = ? THEN 1 ELSE 0 END) AS liked_by_current_user
            FROM forum_posts
            JOIN users ON users.id = forum_posts.user_id
            LEFT JOIN forum_comments ON forum_comments.post_id = forum_posts.id
            LEFT JOIN forum_post_likes ON forum_post_likes.post_id = forum_posts.id
            GROUP BY forum_posts.id, users.username, users.uuid, users.avatar_path
            ORDER BY {order_clause}
            LIMIT ?
            """,
            (user_id or -1, limit),
        ).fetchall()
        post_ids = [row["id"] for row in rows]
        comment_map = {post_id: [] for post_id in post_ids}
        if post_ids:
            placeholders = ",".join(["?"] * len(post_ids))
            comment_rows = db.execute(
                f"""
                SELECT forum_comments.id, forum_comments.post_id, forum_comments.content, forum_comments.created_at,
                       forum_comments.user_id, users.username, users.uuid, users.avatar_path
                FROM forum_comments
                JOIN users ON users.id = forum_comments.user_id
                WHERE forum_comments.post_id IN ({placeholders})
                ORDER BY forum_comments.created_at ASC, forum_comments.id ASC
                """,
                tuple(post_ids),
            ).fetchall()
            for row in comment_rows:
                comment_map.setdefault(row["post_id"], []).append(
                    {
                        "id": row["id"],
                        "post_id": row["post_id"],
                        "content": row["content"],
                        "created_at": row["created_at"],
                        "user_id": row["user_id"],
                        "username": row["username"],
                        "uuid": row["uuid"],
                        "avatar_url": _user_avatar_url(row["avatar_path"]),
                    }
                )
        return success_response(
            "论坛帖子获取成功",
            data={
                "items": [
                    {
                        "id": row["id"],
                        "content": row["content"],
                        "image_url": _forum_image_url(row["image_path"]),
                        "image_name": row["image_name"] or "",
                        "created_at": row["created_at"],
                        "user_id": row["user_id"],
                        "username": row["username"],
                        "uuid": row["uuid"],
                        "avatar_url": _user_avatar_url(row["avatar_path"]),
                        "comment_count": row["comment_count"] or 0,
                        "like_count": row["like_count"] or 0,
                        "liked_by_current_user": bool(row["liked_by_current_user"]),
                        "comments": comment_map.get(row["id"], []),
                    }
                    for row in rows
                ],
                "sort_by": sort_by,
            },
        )
    except Exception as exc:
        return error_response(f"论坛帖子获取失败：{exc}", status=500)


@app.route("/api/forum/posts", methods=["POST"])
@login_required
def create_forum_post():
    try:
        user_id = _current_user_id()
        if request.content_type and "multipart/form-data" in request.content_type:
            content = str(request.form.get("content", "") or "").strip()
            image_file = request.files.get("image")
        else:
            payload = request.get_json(silent=True) or {}
            content = str(payload.get("content", "") or "").strip()
            image_file = None
        if not content and not image_file:
            return error_response("请输入帖子内容或上传图片", status=400)
        if len(content) > 2000:
            return error_response("帖子内容不能超过 2000 字", status=400)

        image_relative_path = ""
        image_name = ""
        if image_file and image_file.filename:
            suffix, original_name = _validated_image_suffix(image_file)
            image_name = original_name
            image_relative_path = f"{uuid.uuid4().hex}{suffix}"
            image_file.save(FORUM_UPLOAD_DIR / image_relative_path)

        db = get_db()
        cursor = db.execute(
            "INSERT INTO forum_posts (user_id, content, image_path, image_name) VALUES (?, ?, ?, ?)",
            (user_id, content, image_relative_path or None, image_name or None),
        )
        db.commit()
        created = db.execute(
            """
            SELECT forum_posts.id, forum_posts.content, forum_posts.image_path, forum_posts.image_name,
                   forum_posts.created_at, forum_posts.user_id,
                   users.username, users.uuid, users.avatar_path
            FROM forum_posts
            JOIN users ON users.id = forum_posts.user_id
            WHERE forum_posts.id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        return success_response(
            "发帖成功",
            data={
                "post": {
                    "id": created["id"],
                    "content": created["content"],
                    "image_url": _forum_image_url(created["image_path"]),
                    "image_name": created["image_name"] or "",
                    "created_at": created["created_at"],
                    "user_id": created["user_id"],
                    "username": created["username"],
                    "uuid": created["uuid"],
                    "avatar_url": _user_avatar_url(created["avatar_path"]),
                }
            },
        )
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"发帖失败：{exc}", status=500)


@app.route("/api/forum/comments", methods=["POST"])
@login_required
def create_forum_comment():
    try:
        payload = request.get_json(silent=True) or {}
        user_id = _current_user_id()
        post_id = payload.get("post_id")
        content = str(payload.get("content", "") or "").strip()
        if not post_id:
            return error_response("缺少帖子 ID", status=400)
        if not content:
            return error_response("请输入评论内容", status=400)
        if len(content) > 1000:
            return error_response("评论内容不能超过 1000 字", status=400)

        db = get_db()
        post = db.execute("SELECT id FROM forum_posts WHERE id = ?", (post_id,)).fetchone()
        if not post:
            return error_response("帖子不存在", status=404)

        cursor = db.execute(
            "INSERT INTO forum_comments (post_id, user_id, content) VALUES (?, ?, ?)",
            (post_id, user_id, content),
        )
        db.commit()
        created = db.execute(
            """
            SELECT forum_comments.id, forum_comments.post_id, forum_comments.content, forum_comments.created_at,
                   forum_comments.user_id, users.username, users.uuid, users.avatar_path
            FROM forum_comments
            JOIN users ON users.id = forum_comments.user_id
            WHERE forum_comments.id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        return success_response(
            "评论成功",
            data={
                "comment": {
                    "id": created["id"],
                    "post_id": created["post_id"],
                    "content": created["content"],
                    "created_at": created["created_at"],
                    "user_id": created["user_id"],
                    "username": created["username"],
                    "uuid": created["uuid"],
                    "avatar_url": _user_avatar_url(created["avatar_path"]),
                }
            },
        )
    except Exception as exc:
        return error_response(f"评论失败：{exc}", status=500)


@app.route("/api/forum/posts/<int:post_id>/like", methods=["POST"])
@login_required
def toggle_forum_like(post_id):
    try:
        user_id = _current_user_id()

        db = get_db()
        post = db.execute("SELECT id FROM forum_posts WHERE id = ?", (post_id,)).fetchone()
        if not post:
            return error_response("帖子不存在", status=404)

        existing = db.execute(
            "SELECT id FROM forum_post_likes WHERE post_id = ? AND user_id = ?",
            (post_id, user_id),
        ).fetchone()
        liked = False
        if existing:
            db.execute("DELETE FROM forum_post_likes WHERE id = ?", (existing["id"],))
        else:
            db.execute(
                "INSERT INTO forum_post_likes (post_id, user_id) VALUES (?, ?)",
                (post_id, user_id),
            )
            liked = True
        db.commit()
        count_row = db.execute(
            "SELECT COUNT(*) AS like_count FROM forum_post_likes WHERE post_id = ?",
            (post_id,),
        ).fetchone()
        return success_response(
            "点赞状态更新成功",
            data={
                "post_id": post_id,
                "liked": liked,
                "like_count": count_row["like_count"] if count_row else 0,
            },
        )
    except Exception as exc:
        return error_response(f"点赞失败：{exc}", status=500)


@app.route("/api/delete_stock", methods=["POST"])
@login_required
def delete_stock():
    try:
        payload = request.get_json(silent=True) or {}
        deleted = delete_user_stock(
            user_id=_current_user_id(),
            stock_code=payload.get("stock_code"),
        )
        if not deleted:
            return error_response("该股票不在自选列表中", status=404)
        return success_response("删除成功")
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:
        return error_response(f"服务器错误：{exc}", status=500)


@app.route("/api/add_test_user", methods=["POST"])
@admin_required
def add_test_user():
    if not _env_flag("ENABLE_TEST_ENDPOINTS", False):
        return error_response("接口不存在", status=404)
    test_password = os.environ.get("TEST_USER_PASSWORD", "").strip()
    if not test_password:
        return error_response("启用测试接口时必须配置 TEST_USER_PASSWORD", status=400)
    if create_test_user(test_password):
        return success_response("测试用户创建成功")
    return error_response("测试用户已存在", status=409)


def _env_flag(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _should_start_scheduler_on_import():
    if not _env_flag("ENABLE_REPORT_SCHEDULER", False):
        return False
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        return True
    return __name__ != "__main__"


if _should_start_scheduler_on_import():
    start_report_scheduler()


if __name__ == "__main__":
    debug_mode = _env_flag("FLASK_DEBUG", False)
    if _env_flag("ENABLE_REPORT_SCHEDULER", True) and ((not debug_mode) or os.environ.get("WERKZEUG_RUN_MAIN") == "true"):
        start_report_scheduler()
    app.run(debug=debug_mode, host="0.0.0.0", port=int(os.environ.get("PORT", "5001")))
