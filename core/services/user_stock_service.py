import json
import hmac
import random
import re
import sqlite3
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

from core.app_settings import ADMIN_SETTINGS
from core.db import get_db
from core.config import REPORT_JSON_DIR
from data_sources.akshare_provider import get_stock_directory_snapshot


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
RESERVED_NUMERIC_USERNAME_PATTERN = re.compile(r"^\d{1,3}$")
ADMIN_USERNAME = ADMIN_SETTINGS.username
SCHEDULE_TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


def _get_user_row(user_id):
    db = get_db()
    row = db.execute(
        """
        SELECT
            id,
            uuid,
            username,
            password,
            email,
            llm_system_prompt,
            llm_user_prompt,
            report_schedule_enabled,
            report_schedule_time,
            report_schedule_stock_codes,
            report_schedule_last_sent_at,
            avatar_path,
            avatar_name,
            approval_status,
            is_admin
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()
    return row


def _ensure_user_exists(user_id):
    if not user_id:
        raise ValueError("缺少user_id参数")
    row = _get_user_row(user_id)
    if not row:
        raise ValueError("用户不存在")
    return row


def _public_user_payload(row):
    if not row:
        return None
    keys = set(row.keys())
    return {
        "id": row["id"],
        "uuid": row["uuid"],
        "username": row["username"],
        "email": row["email"],
        "avatar_path": row["avatar_path"] if "avatar_path" in keys else "",
        "avatar_name": row["avatar_name"] if "avatar_name" in keys else "",
        "is_admin": bool(row["is_admin"]),
        "approval_status": row["approval_status"] or "approved",
    }


def _normalize_schedule_stock_codes(stock_codes):
    if stock_codes is None:
        raw_items = []
    elif isinstance(stock_codes, str):
        raw_items = [item.strip() for item in stock_codes.split(",")]
    else:
        raw_items = [str(item or "").strip() for item in stock_codes]

    normalized = []
    seen = set()
    for item in raw_items:
        if not item or item in seen:
            continue
        seen.add(item)
        normalized.append(item)
    return normalized


def _parse_schedule_stock_codes(raw_value):
    text = str(raw_value or "").strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return _normalize_schedule_stock_codes(text)
    return _normalize_schedule_stock_codes(parsed)


def is_valid_email(value):
    return bool(EMAIL_PATTERN.match(str(value or "").strip()))


def is_reserved_numeric_username(value):
    return bool(RESERVED_NUMERIC_USERNAME_PATTERN.match(str(value or "").strip()))


def _generate_unique_uuid():
    db = get_db()
    existing = {row["uuid"] for row in db.execute("SELECT uuid FROM users WHERE uuid IS NOT NULL").fetchall()}
    for _ in range(2000):
        candidate = random.randint(100, 999)
        if candidate not in existing:
            return candidate
    raise RuntimeError("UUID 分配失败，请稍后重试")


def register_user(username, password, email):
    username = str(username or "").strip()
    password = str(password or "").strip()
    email = str(email or "").strip()
    if not username:
        raise ValueError("请输入账号")
    if is_reserved_numeric_username(username):
        raise ValueError("账号不能是一位、两位或三位纯数字")
    if not password:
        raise ValueError("请输入密码")
    if not email:
        raise ValueError("请输入邮箱")
    if not is_valid_email(email):
        raise ValueError("邮箱格式不正确")

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        raise ValueError("该账号已注册")
    email_existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if email_existing:
        raise ValueError("该邮箱已注册")

    user_uuid = 1 if username == ADMIN_USERNAME else _generate_unique_uuid()
    is_admin = 1 if username == ADMIN_USERNAME else 0
    approval_status = "approved" if is_admin else "pending"
    cursor = db.execute(
        "INSERT INTO users (uuid, username, password, email, is_admin, approval_status) VALUES (?, ?, ?, ?, ?, ?)",
        (user_uuid, username, generate_password_hash(password), email, is_admin, approval_status),
    )
    db.commit()
    row = db.execute(
        "SELECT id, uuid, username, email, avatar_path, avatar_name, is_admin, approval_status FROM users WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()
    return _public_user_payload(row)


def login_user(username, password):
    username = str(username or "").strip()
    password = str(password or "").strip()
    if not username or not password:
        raise ValueError("请输入账号/邮箱/UUID 和密码")

    db = get_db()
    row = None
    if username.isdigit():
        row = db.execute(
            "SELECT id, uuid, username, password, email, avatar_path, avatar_name, is_admin, approval_status FROM users WHERE uuid = ?",
            (int(username),),
        ).fetchone()
    if row is None and is_valid_email(username):
        row = db.execute(
            "SELECT id, uuid, username, password, email, avatar_path, avatar_name, is_admin, approval_status FROM users WHERE email = ?",
            (username,),
        ).fetchone()
    if row is None:
        row = db.execute(
            "SELECT id, uuid, username, password, email, avatar_path, avatar_name, is_admin, approval_status FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if not row or not check_password_hash(row["password"], password):
        raise ValueError("账号/邮箱/UUID 或密码错误")
    if not row["is_admin"] and (row["approval_status"] or "approved") != "approved":
        raise ValueError("账号注册申请正在等待管理员审核")
    return _public_user_payload(row)


def reset_user_password_by_email(email, password, account_identity=None):
    email = str(email or "").strip()
    password = str(password or "").strip()
    account_identity = str(account_identity or "").strip()
    if not email:
        raise ValueError("请输入邮箱")
    if not is_valid_email(email):
        raise ValueError("邮箱格式不正确")
    if not account_identity:
        raise ValueError("请输入账号或 UUID")
    if not password:
        raise ValueError("请输入新密码")

    db = get_db()
    if account_identity.isdigit():
        row = db.execute(
            "SELECT id FROM users WHERE email = ? AND uuid = ?",
            (email, int(account_identity)),
        ).fetchone()
    else:
        row = db.execute(
            "SELECT id FROM users WHERE email = ? AND username = ?",
            (email, account_identity),
        ).fetchone()
    if not row:
        raise ValueError("邮箱与账号/UUID 不匹配")
    db.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (generate_password_hash(password), row["id"]),
    )
    db.commit()


def get_user_profile(user_id):
    return _public_user_payload(_ensure_user_exists(user_id))


def save_user_profile(user_id, username, avatar_path=None, avatar_name=None):
    user = _ensure_user_exists(user_id)
    next_username = str(username or "").strip()
    if not next_username:
        raise ValueError("请输入账号")
    if is_reserved_numeric_username(next_username):
        raise ValueError("账号不能是一位、两位或三位纯数字")

    db = get_db()
    existing = db.execute(
        "SELECT id FROM users WHERE username = ? AND id != ?",
        (next_username, user["id"]),
    ).fetchone()
    if existing:
        raise ValueError("该账号已被使用")

    if avatar_path:
        db.execute(
            "UPDATE users SET username = ?, avatar_path = ?, avatar_name = ? WHERE id = ?",
            (next_username, str(avatar_path).strip(), str(avatar_name or "").strip(), user["id"]),
        )
    else:
        db.execute(
            "UPDATE users SET username = ? WHERE id = ?",
            (next_username, user["id"]),
        )
    db.commit()
    return _public_user_payload(_get_user_row(user["id"]))


def list_all_users(request_user_id):
    requester = _ensure_user_exists(request_user_id)
    if not requester["is_admin"]:
        raise PermissionError("仅管理员可查看全部用户信息")

    db = get_db()
    report_rows = db.execute("SELECT user_id, report_context_json FROM report_histories").fetchall()
    token_usage_by_user = {}
    for report_row in report_rows:
        try:
            report_context = json.loads(report_row["report_context_json"] or "{}")
        except (TypeError, json.JSONDecodeError):
            report_context = {}
        context_payload = report_context.get("report_context") or report_context
        usage = ((context_payload.get("llm_meta") or {}).get("usage") or {})
        total_tokens = usage.get("total_tokens")
        if total_tokens is None:
            total_tokens = (usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0)
        try:
            token_count = int(float(total_tokens or 0))
        except (TypeError, ValueError):
            token_count = 0
        token_usage_by_user[report_row["user_id"]] = token_usage_by_user.get(report_row["user_id"], 0) + token_count

    rows = db.execute(
        """
        SELECT id, uuid, username, email, is_admin, approval_status
        FROM users
        ORDER BY
            CASE COALESCE(approval_status, 'approved')
                WHEN 'pending' THEN 0
                WHEN 'approved' THEN 1
                ELSE 2
            END,
            id ASC
        """
    ).fetchall()
    return [
        {
            "id": row["id"],
            "uuid": row["uuid"],
            "username": row["username"],
            "email": row["email"],
            "is_admin": bool(row["is_admin"]),
            "approval_status": row["approval_status"] or "approved",
            "token_usage": token_usage_by_user.get(row["id"], 0),
        }
        for row in rows
    ]


def approve_user_registration(request_user_id, target_user_id):
    requester = _ensure_user_exists(request_user_id)
    if not requester["is_admin"]:
        raise PermissionError("仅管理员可审核注册用户")

    target = _ensure_user_exists(target_user_id)
    if bool(target["is_admin"]):
        raise ValueError("管理员账号无需审核")
    if (target["approval_status"] or "approved") == "approved":
        raise ValueError("该用户已通过审核")

    db = get_db()
    db.execute("UPDATE users SET approval_status = ? WHERE id = ?", ("approved", target["id"]))
    db.commit()
    row = db.execute(
        "SELECT id, uuid, username, email, is_admin, approval_status FROM users WHERE id = ?",
        (target["id"],),
    ).fetchone()
    return _public_user_payload(row)


def delete_user_account(request_user_id, target_user_id):
    requester = _ensure_user_exists(request_user_id)
    if not requester["is_admin"]:
        raise PermissionError("仅管理员可注销用户")

    target = _ensure_user_exists(target_user_id)
    if int(target["id"]) == int(requester["id"]):
        raise ValueError("不能注销当前登录的管理员账号")
    if bool(target["is_admin"]):
        raise ValueError("不能注销管理员账号")

    db = get_db()
    db.execute("DELETE FROM report_histories WHERE user_id = ?", (target["id"],))
    db.execute("DELETE FROM user_stocks WHERE user_id = ?", (target["id"],))
    db.execute("DELETE FROM users WHERE id = ?", (target["id"],))
    db.commit()
    return {
        "id": target["id"],
        "username": target["username"],
        "uuid": target["uuid"],
    }


def add_user_stock(user_id, stock_code, stock_name):
    user = _ensure_user_exists(user_id)
    resolved_code, resolved_name = _resolve_stock_identity(stock_code, stock_name)

    db = get_db()
    try:
        db.execute(
            "INSERT INTO user_stocks (user_id, stock_code, stock_name) VALUES (?, ?, ?)",
            (user["id"], resolved_code, resolved_name),
        )
        db.commit()
    except sqlite3.IntegrityError as exc:
        raise sqlite3.IntegrityError("该股票已在自选列表中") from exc


def _resolve_stock_identity(stock_code, stock_name):
    code = str(stock_code or "").strip()
    name = str(stock_name or "").strip()
    if not code and not name:
        raise ValueError("请至少输入股票代码或股票名称")

    directory_df = get_stock_directory_snapshot()
    if directory_df is None or directory_df.empty:
        raise ValueError("代码或名称输入错误")

    working_df = directory_df.copy()
    working_df["代码"] = working_df["代码"].astype(str).str.strip()
    working_df["名称"] = working_df["名称"].astype(str).str.strip()

    matched = working_df
    if code:
        matched = matched[matched["代码"] == code]
    if name:
        exact_name_match = matched[matched["名称"] == name]
        if exact_name_match.empty and not code:
            exact_name_match = working_df[working_df["名称"] == name]
        matched = exact_name_match

    if matched.empty:
        raise ValueError("代码或名称输入错误")

    row = matched.iloc[0]
    return str(row["代码"]).strip(), str(row["名称"]).strip()


def list_user_stocks(user_id):
    user = _ensure_user_exists(user_id)
    db = get_db()
    cursor = db.execute(
        "SELECT id, stock_code, stock_name, add_time FROM user_stocks WHERE user_id = ? ORDER BY add_time DESC",
        (user["id"],),
    )
    return [dict(row) for row in cursor.fetchall()]


def delete_user_stock(user_id, stock_code):
    user = _ensure_user_exists(user_id)
    if not stock_code:
        raise ValueError("参数不全")

    db = get_db()
    cursor = db.execute(
        "DELETE FROM user_stocks WHERE user_id = ? AND stock_code = ?",
        (user["id"], stock_code),
    )
    db.commit()
    return cursor.rowcount > 0


def create_test_user(password):
    password = str(password or "").strip()
    if not password:
        raise ValueError("测试用户密码不能为空")
    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", ("test_user",)).fetchone()
    if existing:
        return False
    db.execute(
        "INSERT INTO users (uuid, username, password, is_admin, approval_status) VALUES (?, ?, ?, ?, ?)",
        (_generate_unique_uuid(), "test_user", generate_password_hash(password), 0, "approved"),
    )
    db.commit()
    return True


def get_user_email(user_id):
    row = _ensure_user_exists(user_id)
    return row["email"]


def save_user_email(user_id, email):
    user = _ensure_user_exists(user_id)
    email = str(email or "").strip()
    if not email:
        raise ValueError("请输入邮箱地址")
    if not is_valid_email(email):
        raise ValueError("邮箱格式不正确")

    db = get_db()
    existing = db.execute(
        "SELECT id FROM users WHERE email = ? AND id != ?",
        (email, user["id"]),
    ).fetchone()
    if existing:
        raise ValueError("该邮箱已被其他账号使用")
    db.execute("UPDATE users SET email = ? WHERE id = ?", (email, user["id"]))
    db.commit()
    return email


def save_email_verification_code(email, code, purpose="register", expire_minutes=10, cooldown_seconds=60):
    email = str(email or "").strip()
    code = str(code or "").strip()
    if not email:
        raise ValueError("请输入邮箱")
    if not is_valid_email(email):
        raise ValueError("邮箱格式不正确")
    if not code:
        raise ValueError("验证码不能为空")

    db = get_db()
    recent = db.execute(
        """
        SELECT id
        FROM email_verification_codes
        WHERE email = ? AND purpose = ?
          AND datetime(created_at) > datetime('now', ?)
        ORDER BY id DESC
        LIMIT 1
        """,
        (email, purpose, f"-{int(cooldown_seconds)} seconds"),
    ).fetchone()
    if recent:
        raise ValueError("验证码发送过于频繁，请稍后再试")

    db.execute(
        "DELETE FROM email_verification_codes WHERE email = ? AND purpose = ?",
        (email, purpose),
    )
    db.execute(
        """
        INSERT INTO email_verification_codes (email, code, purpose, expires_at, verified, attempt_count)
        VALUES (?, ?, ?, ?, 0, 0)
        """,
        (
            email,
            generate_password_hash(code),
            purpose,
            (datetime.now() + timedelta(minutes=expire_minutes)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    db.commit()


def verify_email_code(email, code, purpose="register", mark_used=False):
    email = str(email or "").strip()
    code = str(code or "").strip()
    if not email:
        raise ValueError("请输入邮箱")
    if not code:
        raise ValueError("请输入邮箱验证码")

    db = get_db()
    row = db.execute(
        """
        SELECT id, code, expires_at, verified, attempt_count
        FROM email_verification_codes
        WHERE email = ? AND purpose = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (email, purpose),
    ).fetchone()
    if not row:
        raise ValueError("请先获取邮箱验证码")
    if int(row["verified"] or 0) == 1:
        raise ValueError("该验证码已使用，请重新获取")
    if int(row["attempt_count"] or 0) >= 5:
        raise ValueError("验证码尝试次数过多，请重新获取")
    expires_at = datetime.strptime(str(row["expires_at"]), "%Y-%m-%d %H:%M:%S")
    if expires_at < datetime.now():
        raise ValueError("邮箱验证码已过期，请重新获取")
    stored_code = str(row["code"] or "").strip()
    if stored_code.startswith(("scrypt:", "pbkdf2:")):
        code_matches = check_password_hash(stored_code, code)
    else:
        code_matches = hmac.compare_digest(stored_code, code)
    if not code_matches:
        db.execute(
            "UPDATE email_verification_codes SET attempt_count = attempt_count + 1 WHERE id = ?",
            (row["id"],),
        )
        db.commit()
        raise ValueError("邮箱验证码错误")

    if mark_used:
        db.execute(
            "UPDATE email_verification_codes SET verified = 1 WHERE id = ?",
            (row["id"],),
        )
        db.commit()
    return True


def get_user_llm_prompts(user_id):
    row = _ensure_user_exists(user_id)
    return {
        "system_prompt": row["llm_system_prompt"],
        "user_prompt": row["llm_user_prompt"],
    }


def save_user_llm_prompts(user_id, system_prompt, user_prompt):
    user = _ensure_user_exists(user_id)
    system_prompt = str(system_prompt or "").strip()
    user_prompt = str(user_prompt or "").strip()
    if not system_prompt:
        raise ValueError("System Prompt 不能为空")
    if not user_prompt:
        raise ValueError("User Prompt 不能为空")

    db = get_db()
    db.execute(
        "UPDATE users SET llm_system_prompt = ?, llm_user_prompt = ? WHERE id = ?",
        (system_prompt, user_prompt, user["id"]),
    )
    db.commit()
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }


def get_user_report_schedule_settings(user_id):
    row = _ensure_user_exists(user_id)
    return {
        "enabled": bool(row["report_schedule_enabled"]),
        "time": str(row["report_schedule_time"] or "09:00"),
        "stock_codes": _parse_schedule_stock_codes(row["report_schedule_stock_codes"]),
        "last_sent_at": row["report_schedule_last_sent_at"],
    }


def save_user_report_schedule_settings(user_id, enabled, schedule_time, stock_codes):
    user = _ensure_user_exists(user_id)
    enabled_flag = bool(enabled)
    normalized_time = str(schedule_time or "").strip() or "09:00"
    if not SCHEDULE_TIME_PATTERN.match(normalized_time):
        raise ValueError("定时发送时间格式不正确，请使用 24 小时制 HH:MM")

    normalized_codes = _normalize_schedule_stock_codes(stock_codes)
    user_stocks = list_user_stocks(user["id"])
    valid_codes = {str(item["stock_code"]).strip() for item in user_stocks}

    if enabled_flag and not user["email"]:
        raise ValueError("请先保存接收报告邮箱，再开启定时发送")
    if enabled_flag and not normalized_codes:
        raise ValueError("请至少选择一只股票用于定时发送")

    invalid_codes = [code for code in normalized_codes if code not in valid_codes]
    if invalid_codes:
        raise ValueError(f"存在不在自选股中的股票：{', '.join(invalid_codes)}")

    db = get_db()
    db.execute(
        """
        UPDATE users
        SET report_schedule_enabled = ?,
            report_schedule_time = ?,
            report_schedule_stock_codes = ?
        WHERE id = ?
        """,
        (
            1 if enabled_flag else 0,
            normalized_time,
            json.dumps(normalized_codes, ensure_ascii=False),
            user["id"],
        ),
    )
    db.commit()
    return get_user_report_schedule_settings(user["id"])


def list_due_report_schedule_users(schedule_time, current_date):
    normalized_time = str(schedule_time or "").strip()
    normalized_date = str(current_date or "").strip()
    if not normalized_time or not normalized_date:
        return []

    db = get_db()
    rows = db.execute(
        """
        SELECT
            id,
            uuid,
            username,
            email,
            report_schedule_enabled,
            report_schedule_time,
            report_schedule_stock_codes,
            report_schedule_last_sent_at
        FROM users
        WHERE report_schedule_enabled = 1
          AND report_schedule_time = ?
          AND email IS NOT NULL
          AND TRIM(email) != ''
          AND (
                report_schedule_last_sent_at IS NULL
                OR SUBSTR(report_schedule_last_sent_at, 1, 10) != ?
          )
        ORDER BY id ASC
        """,
        (normalized_time, normalized_date),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "uuid": row["uuid"],
            "username": row["username"],
            "email": row["email"],
            "time": row["report_schedule_time"],
            "stock_codes": _parse_schedule_stock_codes(row["report_schedule_stock_codes"]),
            "last_sent_at": row["report_schedule_last_sent_at"],
        }
        for row in rows
    ]


def mark_user_report_schedule_sent(user_id, sent_at=None):
    user = _ensure_user_exists(user_id)
    normalized_sent_at = str(sent_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")).strip()
    db = get_db()
    db.execute(
        "UPDATE users SET report_schedule_last_sent_at = ? WHERE id = ?",
        (normalized_sent_at, user["id"]),
    )
    db.commit()
    return normalized_sent_at


def save_generated_report(user_id, stock_code, stock_name, report_title, report_html, report_context, report_payload=None):
    user = _ensure_user_exists(user_id)
    saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_payload = {
        "schema_version": 1,
        "saved_at": saved_at,
        "user": {
            "id": user["id"],
            "uuid": user["uuid"],
            "username": user["username"],
        },
        "stock_code": str(stock_code or "").strip(),
        "stock_name": str(stock_name or "").strip(),
        "report_title": str(report_title or "").strip(),
        "report_context": report_context or {},
        "analysis_payload": report_payload or {},
    }

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO report_histories (user_id, stock_code, stock_name, report_title, report_html, report_context_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user["id"],
            str(stock_code or "").strip(),
            str(stock_name or "").strip(),
            str(report_title or "").strip(),
            str(report_html or ""),
            json.dumps(report_payload, ensure_ascii=False),
        ),
    )
    db.commit()

    report_filename = f"{user['uuid']}_{str(stock_code or '').strip()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file = REPORT_JSON_DIR / report_filename
    report_file.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return cursor.lastrowid


def list_report_histories(user_id, stock_code=None):
    user = _ensure_user_exists(user_id)
    db = get_db()
    params = [user["id"]]
    sql = """
        SELECT id, stock_code, stock_name, report_title, report_html, report_context_json, created_at
        FROM report_histories
        WHERE user_id = ?
    """
    if stock_code:
        sql += " AND stock_code = ?"
        params.append(str(stock_code).strip())
    sql += " ORDER BY datetime(created_at) DESC, id DESC"
    rows = db.execute(sql, tuple(params)).fetchall()
    items = []
    for row in rows:
        payload = json.loads(row["report_context_json"] or "{}")
        items.append(
            {
                "id": row["id"],
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "report_title": row["report_title"],
                "report_html": row["report_html"],
                "report_context": payload.get("report_context", payload),
                "report_payload": payload,
                "created_at": row["created_at"],
            }
        )
    return items


def get_report_history(user_id, history_id):
    user = _ensure_user_exists(user_id)
    db = get_db()
    row = db.execute(
        """
        SELECT id, stock_code, stock_name, report_title, report_html, report_context_json, created_at
        FROM report_histories
        WHERE id = ? AND user_id = ?
        """,
        (history_id, user["id"]),
    ).fetchone()
    if not row:
        raise ValueError("历史报告不存在")
    payload = json.loads(row["report_context_json"] or "{}")
    return {
        "id": row["id"],
        "stock_code": row["stock_code"],
        "stock_name": row["stock_name"],
        "report_title": row["report_title"],
        "report_html": row["report_html"],
        "report_context": payload.get("report_context", payload),
        "report_payload": payload,
        "created_at": row["created_at"],
    }
