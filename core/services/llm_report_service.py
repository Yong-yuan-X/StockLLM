import json
import logging
import re
import time
from datetime import datetime, timedelta

import pandas as pd

from ai.doubao_helper import ARK_MODEL, call_ark_model_via_openai_sdk
from ai.xiaomi_helper import XIAOMI_MODEL, call_xiaomi_model_via_openai_sdk
from core.app_settings import REPORT_ENABLE_WEB_SEARCH, REPORT_LLM_PROVIDER
from core.services.analysis_service import load_latest_stock_dataframe
from core.services.market_service import fetch_stock_directory
from core.services.user_stock_service import get_user_llm_prompts
from data_sources.market_index import get_market_index_data
from process.common import price_change_pct, round_value
from sentiment.services.sentiment_service import (
    fetch_market_sentiment,
    fetch_sector_sentiment,
    fetch_stock_sentiment,
)


DEFAULT_SYSTEM_PROMPT = """你是一名严谨的A股股票分析报告助手。

你的任务是基于提供的结构化分析 JSON、以及仅包含标题的舆情信息，输出一份用于股票报告页面填充的 JSON。

必须遵守以下规则：
1. 只能依据用户提供的数据进行分析，不要虚构公司基本面、业绩、估值或政策信息。
2. 舆情数据只有标题，没有正文，因此只能作为情绪和关注点线索，不能把标题内容当作已证实事实。
3. 结论要克制、专业、简洁，优先强调趋势、概率、风险和观察位。
4. 如果信息不足，要明确写“信息不足”或“暂无充分依据”，不要编造。
5. 输出必须是合法 JSON，不要输出 Markdown，不要加代码块，不要写 JSON 之外的任何解释。
6. 字段必须完整保留，数组长度尽量控制在 2-4 条，每条一句中文。

输出 JSON 结构如下：
{
  "report_subtitle": "string",
  "rating_title": "string",
  "rating_desc": "string",
  "watch_title": "string",
  "watch_desc": "string",
  "risk_title": "string",
  "risk_desc": "string",
  "conclusion_summary": "string",
  "trend_tag": "string",
  "valuation_tag": "string",
  "action_tag": "string",
  "executive_points": ["string", "string", "string", "string"],
  "positive_signals": ["string", "string", "string"],
  "neutral_observations": ["string", "string", "string"],
  "caution_points": ["string", "string", "string"],
  "market_context_points": ["string", "string", "string"],
  "risk_points": ["string", "string", "string"],
  "ai_summary": "string"
}
"""


DEFAULT_USER_PROMPT = """请基于以下输入，生成股票分析报告填充 JSON。

股票名称：{{stock_name}}
股票代码：{{stock_code}}
预测周期：{{predict_days}} 天
所属板块：{{sector_name}}
报告时间：{{generated_at}}

结构化分析 JSON：
{{analysis_json}}

24小时大盘舆情标题：
{{market_sentiment_titles}}

60天个股舆情标题：
{{stock_sentiment_titles}}

要求：
1. 结论必须体现“规则分析 JSON + 标题舆情”共同作用，但不能夸大舆情结论。
2. trend_tag / valuation_tag / action_tag 要适合直接放入报告标签区，尽量简短。
3. executive_points 要适合放在“执行摘要”里，每条一句。
4. positive_signals / neutral_observations / caution_points / market_context_points / risk_points 都要简洁可读。
5. conclusion_summary 写成 1 段完整中文，建议 120-180 字。
6. ai_summary 写成 1 段完整中文，不少于 300 字，不超过 500 字。
7. 只输出 JSON。
"""

NETWORK_GUARDRAIL_SYSTEM_SUFFIX = """

补充约束：
1. 允许使用联网搜索，但联网结果只能作为辅助验证和补充背景，不能覆盖用户提供的结构化数据。
2. 当联网信息与用户给定数据不一致时，以用户提供的数据为主，并在措辞中保持谨慎。
3. 不要为了使用联网结果而扩展到公司基本面、传闻、论坛观点或未经证实的事件。
4. 联网结果最多只用于验证市场环境、补充公开背景、避免明显过时结论，不要让报告主体偏离输入数据。
"""

NETWORK_GUARDRAIL_USER_SUFFIX = """

补充要求：
7. 如果你使用了联网结果，只能把它当作辅助验证，不要让联网信息替代输入 JSON 与舆情标题。
8. 报告主体必须仍然围绕输入的量化分析结果展开。
"""

OFFLINE_GUARDRAIL_SYSTEM_SUFFIX = """

补充约束：
1. 本次调用不启用联网搜索，只能依据用户提供的结构化数据和舆情标题生成报告。
2. 不要补充未在输入中出现的公司基本面、业绩、估值、政策或突发事件。
3. 如果信息不足，要明确保持谨慎，不要为了完整性编造外部事实。
"""

OFFLINE_GUARDRAIL_USER_SUFFIX = """

补充要求：
7. 不要声称你查询了实时信息或联网资料。
8. 报告主体必须围绕输入的量化分析结果和标题级舆情线索展开。
"""

LLM_MAX_ATTEMPTS = 3
LLM_MIN_WAIT_SECONDS = 10
LLM_RETRY_DELAY_SECONDS = 2

SUPPORTED_REPORT_LLM_PROVIDERS = {"doubao", "xiaomi"}


logger = logging.getLogger(__name__)


def _replace_prompt_vars(template, context):
    rendered = str(template or "")
    for key, value in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
    return rendered


def _truncate_text(value, max_length=1200):
    text = str(value or "").strip()
    if len(text) <= max_length:
        return text
    return f"{text[:max_length]}..."


def _find_balanced_json_object(text):
    source = str(text or "")
    start = source.find("{")
    if start < 0:
        return None

    in_string = False
    escaped = False
    depth = 0
    for index in range(start, len(source)):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    return None


def _extract_json_object(text):
    raw_text = str(text or "").strip()
    if not raw_text:
        raise ValueError("LLM 返回为空")

    fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw_text, re.S)
    if fenced_match:
        raw_text = fenced_match.group(1).strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    balanced_object = _find_balanced_json_object(raw_text)
    if balanced_object:
        try:
            return json.loads(balanced_object)
        except json.JSONDecodeError:
            pass

    object_match = re.search(r"(\{.*\})", raw_text, re.S)
    if object_match:
        try:
            return json.loads(object_match.group(1))
        except json.JSONDecodeError:
            pass

    error = ValueError(f"LLM 返回不是合法 JSON，原始预览：{_truncate_text(raw_text, 600)}")
    setattr(error, "raw_response_preview", _truncate_text(raw_text, 2000))
    raise error


def _safe_lines(items, limit):
    normalized = []
    for item in items[:limit]:
        title = str(item.get("title", "") or "").strip()
        if title:
            normalized.append(f"- {title}")
    return "\n".join(normalized) if normalized else "- 暂无可用标题"


def _build_analysis_digest(analysis_data):
    aggregate = analysis_data.get("aggregate") or {}
    digest = {
        "stock_code": analysis_data.get("stock_code"),
        "predict_days": analysis_data.get("predict_days"),
        "overall_signal": aggregate.get("overall_signal"),
        "total_score": aggregate.get("total_score"),
        "bullish_count": aggregate.get("bullish_count"),
        "bearish_count": aggregate.get("bearish_count"),
        "neutral_count": aggregate.get("neutral_count"),
        "cases": [],
    }
    for item in analysis_data.get("analysis_results") or []:
        digest["cases"].append(
            {
                "case": item.get("case"),
                "title": item.get("title"),
                "signal": item.get("signal"),
                "score": item.get("score"),
                "summary": item.get("summary"),
            }
        )
    return digest


def _should_retry_llm_response(error):
    response_summary = getattr(error, "response_summary", None) or {}
    if not isinstance(response_summary, dict):
        return "LLM 返回不是合法 JSON" in str(error)
    return (
        "未解析到文本内容" in str(error)
        or "LLM 返回不是合法 JSON" in str(error)
        or response_summary.get("incomplete_reason") == "length"
    )


def _wait_before_retry(attempt_started_at, attempt_number):
    elapsed = max(0.0, time.time() - attempt_started_at)
    remaining = max(0.0, LLM_MIN_WAIT_SECONDS - elapsed)
    extra_delay = LLM_RETRY_DELAY_SECONDS if attempt_number < LLM_MAX_ATTEMPTS else 0
    total_delay = remaining + extra_delay
    if total_delay > 0:
        time.sleep(total_delay)


def _get_report_llm_provider():
    provider = REPORT_LLM_PROVIDER or "doubao"
    if provider not in SUPPORTED_REPORT_LLM_PROVIDERS:
        logger.warning("未知 REPORT_LLM_PROVIDER=%s，回退到 doubao", provider)
        return "doubao"
    return provider


def _get_report_llm_model(provider):
    if provider == "xiaomi":
        return XIAOMI_MODEL
    return ARK_MODEL


def _is_report_web_search_enabled(provider):
    if REPORT_ENABLE_WEB_SEARCH:
        return REPORT_ENABLE_WEB_SEARCH in {"1", "true", "yes", "on"}
    return provider == "doubao"


def _call_report_llm(user_prompt, system_prompt):
    provider = _get_report_llm_provider()
    enable_web_search = _is_report_web_search_enabled(provider)
    if provider == "xiaomi":
        return call_xiaomi_model_via_openai_sdk(
            user_prompt,
            system_prompt=system_prompt,
            max_tokens=2800,
            timeout=180,
            enable_web_search=enable_web_search,
            response_format={"type": "json_object"},
            disable_thinking=True,
            return_metadata=True,
        )

    return call_ark_model_via_openai_sdk(
        user_prompt,
        system_prompt=system_prompt,
        enable_web_search=enable_web_search,
        max_output_tokens=2800,
        timeout=180,
        return_metadata=True,
    )


def _format_signal_label(signal):
    return {
        "bullish": "偏多",
        "bearish": "偏空",
        "neutral": "中性",
    }.get(str(signal or "").strip(), "中性")


def _format_score_label(score):
    score_value = int(score or 0)
    return f"{score_value:+d}"


def _pick_metric_value(result):
    details = result.get("details") or {}
    value_candidates = [
        ("bullish_probability", lambda value: f"上涨概率 {round_value(value, 2)}%"),
        ("predicted_price", lambda value: f"预测价 {round_value(value, 2)}"),
        ("projected_price", lambda value: f"预测价 {round_value(value, 2)}"),
        ("rsi", lambda value: f"RSI {round_value(value, 2)}"),
        ("adx", lambda value: f"ADX {round_value(value, 2)}"),
        ("latest_close", lambda value: f"最新价 {round_value(value, 2)}"),
    ]
    for key, formatter in value_candidates:
        value = details.get(key)
        if value is not None:
            try:
                return formatter(value)
            except Exception:
                continue
    return f"{_format_signal_label(result.get('signal'))} / 分值 {_format_score_label(result.get('score'))}"


def _format_amount_yi(value):
    if value is None or pd.isna(value):
        return "--"
    return f"{round(float(value) / 100000000, 2)} 亿"


def _build_candlestick_svg(df, limit=60):
    working_df = df.tail(min(limit, len(df))).copy()
    if working_df.empty:
        return ""

    width = 920
    height = 320
    padding_x = 30
    padding_y = 22
    min_price = float(working_df["low"].min())
    max_price = float(working_df["high"].max())
    value_range = max(max_price - min_price, 0.01)
    candle_gap = (width - padding_x * 2) / max(len(working_df), 1)
    candle_width = max(4, min(10, candle_gap * 0.55))

    def map_y(value):
        return height - padding_y - ((float(value) - min_price) / value_range) * (height - padding_y * 2)

    elements = [
        f'<line x1="{padding_x}" y1="{padding_y}" x2="{padding_x}" y2="{height - padding_y}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>',
        f'<line x1="{padding_x}" y1="{height - padding_y}" x2="{width - padding_x}" y2="{height - padding_y}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>',
    ]
    for index, (_, row) in enumerate(working_df.iterrows()):
        x = padding_x + candle_gap * index + candle_gap / 2
        open_price = float(row["open"]) if pd.notna(row.get("open")) else float(row["close"])
        close_price = float(row["close"])
        high_price = float(row["high"]) if pd.notna(row.get("high")) else max(open_price, close_price)
        low_price = float(row["low"]) if pd.notna(row.get("low")) else min(open_price, close_price)
        color = "#dc2626" if close_price >= open_price else "#16a34a"
        body_top = min(map_y(open_price), map_y(close_price))
        body_bottom = max(map_y(open_price), map_y(close_price))
        body_height = max(2, body_bottom - body_top)
        elements.append(f'<line x1="{x:.2f}" y1="{map_y(low_price):.2f}" x2="{x:.2f}" y2="{map_y(high_price):.2f}" stroke="{color}" stroke-width="1.6"></line>')
        elements.append(f'<rect x="{(x - candle_width / 2):.2f}" y="{body_top:.2f}" width="{candle_width:.2f}" height="{body_height:.2f}" rx="2" fill="{color}" opacity="0.9"></rect>')
    return f'<svg viewBox="0 0 {width} {height}" class="report-chart-svg" preserveAspectRatio="none">{"".join(elements)}</svg>'


def _build_volume_svg(df, limit=30):
    working_df = df.tail(min(limit, len(df))).copy()
    if working_df.empty:
        return ""

    width = 920
    height = 260
    padding_x = 28
    padding_y = 20
    max_volume = max(float(working_df["volume"].fillna(0).max()), 1.0)
    bar_gap = (width - padding_x * 2) / max(len(working_df), 1)
    bar_width = max(6, min(16, bar_gap * 0.65))
    elements = [
        f'<line x1="{padding_x}" y1="{height - padding_y}" x2="{width - padding_x}" y2="{height - padding_y}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>'
    ]
    for index, (_, row) in enumerate(working_df.iterrows()):
        x = padding_x + bar_gap * index + (bar_gap - bar_width) / 2
        volume = float(row["volume"]) if pd.notna(row.get("volume")) else 0.0
        open_price = float(row["open"]) if pd.notna(row.get("open")) else float(row["close"])
        close_price = float(row["close"])
        color = "#dc2626" if close_price >= open_price else "#16a34a"
        bar_height = max(2, (volume / max_volume) * (height - padding_y * 2))
        y = height - padding_y - bar_height
        elements.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" rx="3" fill="{color}" opacity="0.88"></rect>')
    return f'<svg viewBox="0 0 {width} {height}" class="report-chart-svg" preserveAspectRatio="none">{"".join(elements)}</svg>'


def _build_compare_svg(stock_series, market_series):
    if not stock_series or not market_series:
        return ""

    width = 920
    height = 260
    padding_x = 28
    padding_y = 22

    stock_values = [float(item["close"]) for item in stock_series if item.get("close") is not None]
    market_values = [float(item["close"]) for item in market_series if item.get("close") is not None]
    if not stock_values or not market_values:
        return ""

    stock_base = stock_values[0]
    market_base = market_values[0]
    stock_norm = [value / stock_base * 100 for value in stock_values]
    market_norm = [value / market_base * 100 for value in market_values]
    all_values = stock_norm + market_norm
    min_value = min(all_values)
    max_value = max(all_values)
    value_range = max(max_value - min_value, 0.01)

    def build_path(values):
        points = []
        for index, value in enumerate(values):
            x = padding_x + index * (width - padding_x * 2) / max(len(values) - 1, 1)
            y = height - padding_y - ((value - min_value) / value_range) * (height - padding_y * 2)
            points.append((x, y))
        return " ".join(f'{"M" if idx == 0 else "L"} {point[0]:.2f} {point[1]:.2f}' for idx, point in enumerate(points))

    stock_path = build_path(stock_norm)
    market_path = build_path(market_norm)
    return (
        f'<svg viewBox="0 0 {width} {height}" class="report-chart-svg" preserveAspectRatio="none">'
        f'<line x1="{padding_x}" y1="{padding_y}" x2="{padding_x}" y2="{height - padding_y}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>'
        f'<line x1="{padding_x}" y1="{height - padding_y}" x2="{width - padding_x}" y2="{height - padding_y}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>'
        f'<path d="{market_path}" fill="none" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>'
        f'<path d="{stock_path}" fill="none" stroke="#2563eb" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>'
        f'</svg>'
    )


def _build_metrics_rows(analysis_results):
    allowed_cases = {"ma", "rsi", "macd", "arima", "xgboost"}
    interpretation_suffix = {
        "bullish": "这说明当前模块给出的短线判断相对积极，但仍需要结合量价配合与后续走势确认信号是否延续，避免仅凭单一结果直接下结论。",
        "bearish": "这说明当前模块对短线表现保持谨慎，后续应继续观察关键支撑、量能变化以及市场情绪是否出现新的修复迹象。",
        "neutral": "这说明当前模块暂未给出特别明确的单边倾向，实际判断还需要结合其他指标、市场环境与后续价格行为共同确认。",
    }
    rows = []
    for item in analysis_results:
        case_name = str(item.get("case") or "").strip().lower()
        if case_name not in allowed_cases:
            continue
        base_summary = str(item.get("summary") or "暂无解读").strip()
        rows.append(
            {
                "indicator": item.get("title", item.get("case", "未知指标")),
                "current_value": _pick_metric_value(item),
                "interpretation": f"{base_summary}{interpretation_suffix.get(item.get('signal'), interpretation_suffix['neutral'])}",
            }
        )
    return rows


def _resolve_stock_profile(stock_code):
    normalized_code = str(stock_code).strip()
    if normalized_code in INDEX_NAME_MAP:
        return {
            "stock_code": normalized_code,
            "stock_name": INDEX_NAME_MAP[normalized_code],
            "market": "A股指数",
            "sector_name": "大盘指数",
        }
    try:
        response = fetch_stock_directory(keyword=stock_code, page=1, page_size=1)
        items = response.get("items") or []
        if items:
            item = items[0]
            return {
                "stock_code": str(item.get("code", stock_code) or stock_code).strip(),
                "stock_name": str(item.get("name", "") or "").strip() or str(stock_code),
                "market": str(item.get("market", "") or "").strip(),
                "sector_name": str(item.get("industry", "") or "").strip(),
            }
    except Exception:
        pass
    return {
        "stock_code": str(stock_code).strip(),
        "stock_name": str(stock_code).strip(),
        "market": "",
        "sector_name": "",
    }


def _build_sentiment_context(stock_code, sector_name):
    end_time = datetime.now()
    timing_breakdown = {}
    market = {"items": [], "target": "A股市场"}
    market_started_at = time.perf_counter()
    try:
        market = fetch_market_sentiment(
            days=1,
            start_time=(end_time - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
        )
    except Exception:
        market = {"items": [], "target": "A股市场"}
    timing_breakdown["market_sentiment_seconds"] = round(time.perf_counter() - market_started_at, 3)

    sector = {"items": [], "target": sector_name or "未识别板块"}
    if sector_name:
        sector_started_at = time.perf_counter()
        try:
            sector = fetch_sector_sentiment(
                sector_name,
                days=2,
                start_time=(end_time - timedelta(hours=48)).strftime("%Y-%m-%d %H:%M:%S"),
                end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception:
            sector = {"items": [], "target": sector_name}
        timing_breakdown["sector_sentiment_seconds"] = round(time.perf_counter() - sector_started_at, 3)
    else:
        timing_breakdown["sector_sentiment_seconds"] = 0.0

    stock = {"items": [], "target": stock_code}
    stock_started_at = time.perf_counter()
    try:
        stock = fetch_stock_sentiment(
            stock_code,
            days=60,
            start_time=(end_time - timedelta(days=60)).strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
        )
    except Exception:
        stock = {"items": [], "target": stock_code}
    timing_breakdown["stock_sentiment_seconds"] = round(time.perf_counter() - stock_started_at, 3)
    timing_breakdown["total_seconds"] = round(sum(timing_breakdown.values()), 3)
    return {
        "market": market,
        "sector": sector,
        "stock": stock,
    }, timing_breakdown


def _build_programmatic_sections(analysis_data, stock_df, stock_profile, sentiment_context):
    latest_row = stock_df.iloc[-1]
    lookback_df = stock_df.tail(min(90, len(stock_df))).copy()
    period_return = price_change_pct(lookback_df.iloc[0]["close"], lookback_df.iloc[-1]["close"]) if not lookback_df.empty else None
    period_high = round_value(lookback_df["high"].max(), 2) if "high" in lookback_df.columns and not lookback_df.empty else None
    period_low = round_value(lookback_df["low"].min(), 2) if "low" in lookback_df.columns and not lookback_df.empty else None

    market_data = {"indices": []}
    try:
        market_data = get_market_index_data(days=90, k_type="day")
    except Exception:
        market_data = {"indices": []}
    sh_index = next((item for item in market_data.get("indices", []) if item.get("key") == "sh000001"), None)
    sh_return = None
    if sh_index and sh_index.get("series"):
        series = sh_index["series"]
        sh_return = price_change_pct(series[0]["close"], series[-1]["close"])

    relative_strength = None
    relative_strength_label = "待观察"
    if period_return is not None and sh_return is not None:
        relative_strength = round_value(period_return - sh_return, 2)
        if relative_strength >= 2:
            relative_strength_label = "跑赢"
        elif relative_strength <= -2:
            relative_strength_label = "跑输"
        else:
            relative_strength_label = "接近同步"

    aggregate = analysis_data.get("aggregate") or {}
    overall_signal = str(aggregate.get("overall_signal", "neutral"))
    rating_title = {
        "bullish": "偏多观察",
        "bearish": "谨慎防守",
        "neutral": "中性跟踪",
    }.get(overall_signal, "中性跟踪")

    watch_title = f"{round_value(period_high, 2) or round_value(latest_row['close'], 2)} 压力位"
    risk_title = "波动放大"
    report_charts = {
        "price_svg": _build_candlestick_svg(lookback_df, limit=60),
        "volume_svg": _build_volume_svg(lookback_df, limit=30),
        "compare_svg": _build_compare_svg(
            [
                {"date": row["trade_date"].strftime("%Y-%m-%d"), "close": round(float(row["close"]), 2)}
                for _, row in lookback_df.iterrows()
            ],
            sh_index.get("series", []) if sh_index else [],
        ),
    }

    return {
        "header": {
            "stock_name": stock_profile["stock_name"],
            "stock_code": stock_profile["stock_code"],
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "predict_days": analysis_data.get("predict_days"),
            "version": "LLM Report v1",
            "subtitle": "基于历史行情、规则指标、机器学习信号与标题级舆情生成的结构化报告",
        },
        "summary_cards": {
            "latest_price": round_value(latest_row["close"], 2),
            "latest_pct_chg": round_value(latest_row.get("pct_chg"), 2),
            "period_return": round_value(period_return, 2),
            "latest_amount": _format_amount_yi(latest_row.get("amount")),
            "relative_strength_label": relative_strength_label,
            "relative_strength_value": relative_strength,
            "period_high": period_high,
            "period_low": period_low,
        },
        "ribbon_defaults": {
            "rating_title": rating_title,
            "rating_desc": f"综合 {aggregate.get('bullish_count', 0)} 个偏多、{aggregate.get('neutral_count', 0)} 个中性、{aggregate.get('bearish_count', 0)} 个偏空信号得到当前判断。",
            "watch_title": watch_title,
            "watch_desc": f"近 90 个交易日区间高点约为 {period_high or '--'}，需观察突破确认。",
            "risk_title": risk_title,
            "risk_desc": f"近 60 天个股舆情共 {len(sentiment_context['stock'].get('items', []))} 条，若情绪反复，短线波动可能加大。",
        },
        "trend_tag": {
            "bullish": "趋势偏强",
            "bearish": "趋势偏弱",
            "neutral": "震荡观察",
        }.get(overall_signal, "震荡观察"),
        "valuation_tag": "信息不足",
        "action_tag": {
            "bullish": "关注放量延续",
            "bearish": "优先控制回撤",
            "neutral": "等待方向确认",
        }.get(overall_signal, "等待方向确认"),
        "executive_points": [
            f"短期趋势：{_format_signal_label(overall_signal)}",
            f"规则与模型总分：{aggregate.get('total_score', 0)}",
            f"预测周期：{analysis_data.get('predict_days')} 天",
            f"所属板块：{stock_profile.get('sector_name') or '暂未识别'}",
        ],
        "positive_signals": [
            item.get("summary", "暂无积极信号")
            for item in (analysis_data.get("analysis_results") or [])
            if item.get("signal") == "bullish"
        ][:3],
        "neutral_observations": [
            item.get("summary", "暂无中性观察")
            for item in (analysis_data.get("analysis_results") or [])
            if item.get("signal") == "neutral"
        ][:3],
        "caution_points": [
            item.get("summary", "暂无谨慎提示")
            for item in (analysis_data.get("analysis_results") or [])
            if item.get("signal") == "bearish"
        ][:3],
        "market_context_points": [
            f"24 小时大盘舆情标题共 {len(sentiment_context['market'].get('items', []))} 条，可辅助判断市场风险偏好。",
            f"所属板块为 {stock_profile.get('sector_name') or '暂未识别'}，板块联动仍应结合当日轮动强弱与资金偏好进一步确认。",
            f"上证指数近 90 日区间表现约 {round_value(sh_return, 2) if sh_return is not None else '--'}%。",
        ],
        "risk_points": [
            "标题级舆情只能反映关注方向，不能替代正文验证。",
            "模型与规则均基于历史数据，无法直接覆盖突发事件冲击。",
            "若市场进入系统性波动阶段，个股相对强弱可能迅速变化。",
        ],
        "ai_summary_fallback": "当前报告已经基于历史行情、规则指标、机器学习结果以及标题级舆情完成初步整合。整体来看，这份结果更适合作为辅助分析材料，而不是单独的投资决策依据。量化模块能够帮助识别当前价格趋势、动量变化、波动水平与短期方向概率，舆情标题则用于补充市场关注点和风险偏好线索。由于舆情仅保留标题，且模型结论依赖历史数据，因此在阅读报告时仍应重点结合关键支撑压力位、量价变化以及后续市场环境确认信号是否延续。若后续接入稳定可用的大模型，可进一步把这些结构化结果整理为更自然、层次更清晰的报告文本，但风险提示与证据链仍需保留。",
        "charts": report_charts,
        "metrics_rows": _build_metrics_rows(analysis_data.get("analysis_results") or []),
        "sentiment_sections": [
            {
                "title": "24h 大盘舆情",
                "subtitle": "用于感知市场情绪与风险偏好。",
                "items": [item.get("title") for item in sentiment_context["market"].get("items", [])[:8] if item.get("title")],
            },
            {
                "title": "60d 个股舆情",
                "subtitle": f"个股：{stock_profile['stock_code']}",
                "items": [item.get("title") for item in sentiment_context["stock"].get("items", [])[:10] if item.get("title")],
            },
        ],
    }


def _fallback_llm_sections(programmatic, analysis_data):
    positive = programmatic["positive_signals"] or ["暂无明显一致的积极信号，建议结合后续走势确认。"]
    neutral = programmatic["neutral_observations"] or ["当前规则结果中中性信号占比不低，方向确认仍需时间。"]
    caution = programmatic["caution_points"] or ["部分指标未形成一致偏多结论，需警惕震荡反复。"]
    return {
        "report_subtitle": programmatic["header"]["subtitle"],
        "rating_title": programmatic["ribbon_defaults"]["rating_title"],
        "rating_desc": programmatic["ribbon_defaults"]["rating_desc"],
        "watch_title": programmatic["ribbon_defaults"]["watch_title"],
        "watch_desc": programmatic["ribbon_defaults"]["watch_desc"],
        "risk_title": programmatic["ribbon_defaults"]["risk_title"],
        "risk_desc": programmatic["ribbon_defaults"]["risk_desc"],
        "conclusion_summary": f"综合 {len(analysis_data.get('analysis_results') or [])} 个分析模块后，当前结论偏向 {programmatic['trend_tag']}。从已有规则指标、预测模型结果以及市场环境线索来看，短线判断已经具备一定依据，但一致性仍需要后续走势继续验证。建议把观察重点放在量价是否同步、关键支撑与压力位是否被有效确认，以及市场风险偏好是否继续配合，避免在信号尚未完全共振时过早放大预期。",
        "trend_tag": programmatic["trend_tag"],
        "valuation_tag": programmatic["valuation_tag"],
        "action_tag": programmatic["action_tag"],
        "executive_points": programmatic["executive_points"][:4],
        "positive_signals": positive[:3],
        "neutral_observations": neutral[:3],
        "caution_points": caution[:3],
        "market_context_points": programmatic["market_context_points"][:3],
        "risk_points": programmatic["risk_points"][:3],
        "ai_summary": programmatic["ai_summary_fallback"],
    }


def _generate_llm_sections(stock_profile, analysis_data, sentiment_context, user_id, programmatic):
    total_started_at = time.perf_counter()
    prompt_started_at = time.perf_counter()
    provider = _get_report_llm_provider()
    prompts = get_user_llm_prompts(user_id) if user_id else {"system_prompt": None, "user_prompt": None}
    system_prompt = prompts.get("system_prompt") or DEFAULT_SYSTEM_PROMPT
    user_prompt = prompts.get("user_prompt") or DEFAULT_USER_PROMPT

    analysis_digest_json = json.dumps(_build_analysis_digest(analysis_data), ensure_ascii=False, indent=2)
    compact_market_titles = _safe_lines(sentiment_context["market"].get("items", []), 10)
    compact_stock_titles = _safe_lines(sentiment_context["stock"].get("items", []), 12)

    prompt_context = {
        "stock_name": stock_profile["stock_name"],
        "stock_code": stock_profile["stock_code"],
        "predict_days": analysis_data.get("predict_days"),
        "sector_name": stock_profile.get("sector_name") or "暂未识别",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "analysis_json": analysis_digest_json,
        "market_sentiment_titles": compact_market_titles,
        "stock_sentiment_titles": compact_stock_titles,
    }
    rendered_system_prompt = _replace_prompt_vars(system_prompt, prompt_context)
    rendered_user_prompt = _replace_prompt_vars(user_prompt, prompt_context)

    if _is_report_web_search_enabled(provider):
        rendered_system_prompt = f"{rendered_system_prompt.strip()}\n{NETWORK_GUARDRAIL_SYSTEM_SUFFIX.strip()}"
        rendered_user_prompt = f"{rendered_user_prompt.strip()}\n{NETWORK_GUARDRAIL_USER_SUFFIX.strip()}"
    else:
        rendered_system_prompt = f"{rendered_system_prompt.strip()}\n{OFFLINE_GUARDRAIL_SYSTEM_SUFFIX.strip()}"
        rendered_user_prompt = f"{rendered_user_prompt.strip()}\n{OFFLINE_GUARDRAIL_USER_SUFFIX.strip()}"

    retry_note = "\n\n最后要求：直接输出最终 JSON，不要输出思考过程，不要先分析再作答；若长度受限，优先保证 JSON 字段完整，每个列表最多写 2 条。"
    debug_meta = {
        "provider": provider,
        "system_prompt": rendered_system_prompt,
        "user_prompt": rendered_user_prompt,
        "analysis_digest_json": analysis_digest_json,
        "attempts": [],
        "timing_breakdown": {
            "prompt_build_seconds": round(time.perf_counter() - prompt_started_at, 3),
        },
    }
    last_error = None

    for attempt in range(1, LLM_MAX_ATTEMPTS + 1):
        attempt_started_at = time.time()
        attempt_prompt = rendered_user_prompt if attempt == 1 else f"{rendered_user_prompt}{retry_note}"
        try:
            llm_response = _call_report_llm(attempt_prompt, rendered_system_prompt)
            llm_sections = _extract_json_object(llm_response.get("text"))
            debug_meta.update(
                {
                    "raw_response": llm_response.get("text"),
                    "usage": llm_response.get("usage") or {},
                    "provider": provider,
                    "model": llm_response.get("model"),
                    "enable_web_search": llm_response.get("enable_web_search"),
                    "response_summary": llm_response.get("response_summary"),
                    "raw_response_preview": _truncate_text(llm_response.get("text"), 2000),
                    "attempt_count": attempt,
                }
            )
            debug_meta["timing_breakdown"]["total_seconds"] = round(time.perf_counter() - total_started_at, 3)
            debug_meta["attempts"].append(
                {
                    "attempt": attempt,
                    "status": "success",
                    "elapsed_seconds": round(max(0.0, time.time() - attempt_started_at), 2),
                }
            )
            return llm_sections, debug_meta
        except Exception as exc:
            last_error = exc
            debug_meta["attempts"].append(
                {
                    "attempt": attempt,
                    "status": "failed",
                    "error": str(exc),
                    "elapsed_seconds": round(max(0.0, time.time() - attempt_started_at), 2),
                    "response_summary": getattr(exc, "response_summary", None),
                    "raw_response_preview": getattr(exc, "raw_response_preview", None),
                }
            )
            if attempt >= LLM_MAX_ATTEMPTS or not _should_retry_llm_response(exc):
                break
            _wait_before_retry(attempt_started_at, attempt)

    debug_meta["timing_breakdown"]["total_seconds"] = round(time.perf_counter() - total_started_at, 3)
    if last_error is not None:
        setattr(last_error, "llm_attempts", debug_meta["attempts"])
        setattr(last_error, "llm_timing_breakdown", debug_meta["timing_breakdown"])
    raise last_error or RuntimeError("LLM 生成失败")


def build_stock_report_context(stock_code, analysis_data, user_id=None):
    total_started_at = time.perf_counter()
    timing_breakdown = {}

    load_started_at = time.perf_counter()
    stock_df, _ = load_latest_stock_dataframe(stock_code)
    timing_breakdown["load_stock_dataframe_seconds"] = round(time.perf_counter() - load_started_at, 3)
    if stock_df is None or stock_df.empty:
        raise FileNotFoundError(f"未找到 {stock_code} 的历史数据")

    profile_started_at = time.perf_counter()
    stock_profile = _resolve_stock_profile(stock_code)
    timing_breakdown["resolve_stock_profile_seconds"] = round(time.perf_counter() - profile_started_at, 3)

    sentiment_context, sentiment_timing = _build_sentiment_context(stock_code, stock_profile.get("sector_name"))
    timing_breakdown["sentiment_context"] = sentiment_timing

    programmatic_started_at = time.perf_counter()
    programmatic = _build_programmatic_sections(analysis_data, stock_df, stock_profile, sentiment_context)
    timing_breakdown["build_programmatic_sections_seconds"] = round(time.perf_counter() - programmatic_started_at, 3)

    llm_status = "fallback"
    llm_debug = {}
    llm_sections = _fallback_llm_sections(programmatic, analysis_data)
    try:
        llm_started_at = time.perf_counter()
        llm_sections, llm_debug = _generate_llm_sections(
            stock_profile,
            analysis_data,
            sentiment_context,
            user_id,
            programmatic,
        )
        timing_breakdown["llm_generate_seconds"] = round(time.perf_counter() - llm_started_at, 3)
        llm_status = "success"
    except Exception as exc:
        timing_breakdown["llm_generate_seconds"] = round(getattr(exc, "llm_timing_breakdown", {}).get("total_seconds") or 0.0, 3)
        raw_error = str(exc)
        provider = _get_report_llm_provider()
        config_hint = None
        if "InvalidEndpointOrModel.NotFound" in raw_error or "does not exist or you do not have access to it" in raw_error:
            if provider == "xiaomi":
                config_hint = (
                    "当前小米 MiMo 模型/endpoint 不可用。请在 core/app_settings.py 或环境变量 XIAOMI_MODEL 中，"
                    "改成你小米账号里实际可调用的模型。"
                )
            else:
                config_hint = (
                    "当前豆包模型/endpoint 不可用。请在 core/app_settings.py 或环境变量 ARK_MODEL 中，"
                    "改成你火山方舟账号里实际可调用的模型或推理接入点。"
                )
        llm_debug = {
            "error": raw_error,
            "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None},
            "provider": provider,
            "model": _get_report_llm_model(provider),
            "enable_web_search": _is_report_web_search_enabled(provider),
            "response_summary": getattr(exc, "response_summary", None),
            "raw_response_preview": getattr(exc, "raw_response_preview", None),
            "attempts": getattr(exc, "llm_attempts", None),
            "timing_breakdown": getattr(exc, "llm_timing_breakdown", None),
            "config_hint": config_hint,
        }

    timing_breakdown["total_seconds"] = round(time.perf_counter() - total_started_at, 3)
    logger.info(
        "报告构建阶段耗时 stock=%s total=%.3fs load_df=%.3fs profile=%.3fs sentiment=%.3fs programmatic=%.3fs llm=%.3fs",
        stock_code,
        timing_breakdown["total_seconds"],
        timing_breakdown["load_stock_dataframe_seconds"],
        timing_breakdown["resolve_stock_profile_seconds"],
        timing_breakdown["sentiment_context"]["total_seconds"],
        timing_breakdown["build_programmatic_sections_seconds"],
        timing_breakdown["llm_generate_seconds"],
    )

    report_context = {
        "header": programmatic["header"],
        "summary_cards": programmatic["summary_cards"],
        "ribbons": {
            "rating_title": llm_sections.get("rating_title") or programmatic["ribbon_defaults"]["rating_title"],
            "rating_desc": llm_sections.get("rating_desc") or programmatic["ribbon_defaults"]["rating_desc"],
            "watch_title": llm_sections.get("watch_title") or programmatic["ribbon_defaults"]["watch_title"],
            "watch_desc": llm_sections.get("watch_desc") or programmatic["ribbon_defaults"]["watch_desc"],
            "risk_title": llm_sections.get("risk_title") or programmatic["ribbon_defaults"]["risk_title"],
            "risk_desc": llm_sections.get("risk_desc") or programmatic["ribbon_defaults"]["risk_desc"],
        },
        "conclusion_summary": llm_sections.get("conclusion_summary") or _fallback_llm_sections(programmatic, analysis_data)["conclusion_summary"],
        "trend_tag": llm_sections.get("trend_tag") or programmatic["trend_tag"],
        "valuation_tag": llm_sections.get("valuation_tag") or programmatic["valuation_tag"],
        "action_tag": llm_sections.get("action_tag") or programmatic["action_tag"],
        "executive_points": (llm_sections.get("executive_points") or programmatic["executive_points"])[:4],
        "positive_signals": (llm_sections.get("positive_signals") or programmatic["positive_signals"] or ["暂无明显积极信号"])[:3],
        "neutral_observations": (llm_sections.get("neutral_observations") or programmatic["neutral_observations"] or ["暂无明显中性观察"])[:3],
        "caution_points": (llm_sections.get("caution_points") or programmatic["caution_points"] or ["暂无明显谨慎点"])[:3],
        "metrics_rows": programmatic["metrics_rows"],
        "charts": programmatic["charts"],
        "market_context_points": (llm_sections.get("market_context_points") or programmatic["market_context_points"])[:3],
        "risk_points": (llm_sections.get("risk_points") or programmatic["risk_points"])[:3],
        "sentiment_sections": programmatic["sentiment_sections"],
        "ai_summary": llm_sections.get("ai_summary") or programmatic["ai_summary_fallback"],
        "stock_profile": stock_profile,
        "sentiment_context": {
            "market_count": len(sentiment_context["market"].get("items", [])),
            "sector_count": len(sentiment_context["sector"].get("items", [])),
            "stock_count": len(sentiment_context["stock"].get("items", [])),
        },
        "llm_meta": {
            "status": llm_status,
            "debug": llm_debug,
            "usage": (llm_debug or {}).get("usage", {}),
            "model": (llm_debug or {}).get("model"),
            "enable_web_search": (llm_debug or {}).get("enable_web_search"),
            "timing_breakdown": (llm_debug or {}).get("timing_breakdown"),
        },
        "timing_breakdown": timing_breakdown,
    }
    return report_context


def build_demo_report_context():
    return {
        "header": {
            "stock_name": "示例股票",
            "stock_code": "600000",
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "predict_days": 30,
            "version": "Preview v2",
            "subtitle": "这里展示的是可由规则分析 + 舆情标题 + LLM 共同生成的动态报告样式。",
        },
        "summary_cards": {
            "latest_price": "12.34",
            "latest_pct_chg": "+1.28",
            "period_return": "+6.52",
            "latest_amount": "18.6 亿",
            "relative_strength_label": "跑赢",
            "relative_strength_value": "+2.18",
            "period_high": "12.88",
            "period_low": "10.96",
        },
        "ribbons": {
            "rating_title": "偏多观察",
            "rating_desc": "多数规则信号偏多，但仍需确认情绪与量能是否继续配合。",
            "watch_title": "12.88 压力位",
            "watch_desc": "若后续放量突破，短中期结构有望继续改善。",
            "risk_title": "波动放大",
            "risk_desc": "若市场风险偏好回落，短线回撤幅度可能明显加大。",
        },
        "conclusion_summary": "示例报告会把程序直接可得的数据放进固定模板，再把 LLM 的结论摘要、风险提示和舆情归纳嵌进对应模块。扩展后的结论摘要会更完整地解释趋势判断来自哪些规则指标、模型结果和市场背景线索，并明确提醒使用者关注关键价位、量能变化以及后续确认信号，而不是只给出一句非常简短的方向结论。",
        "trend_tag": "趋势偏强",
        "valuation_tag": "信息不足",
        "action_tag": "关注放量延续",
        "executive_points": ["短期趋势：偏强", "中期结构：等待确认", "舆情情绪：中性偏暖", "适合场景：趋势跟踪观察"],
        "positive_signals": ["价格位于中期均线上方。"],
        "neutral_observations": ["标题级舆情对方向有提示意义，但不等同正文证据。"],
        "caution_points": ["接近压力位时需关注缩量冲高。"],
        "metrics_rows": [
            {"indicator": "MA 均线结构", "current_value": "偏多 / 分值 +1", "interpretation": "短中期均线关系较平稳，价格运行位置尚可。这说明均线结构暂时支持当前趋势判断，但后续仍要观察价格能否继续站稳关键均线并得到量能配合。"},
            {"indicator": "XGBoost 分类", "current_value": "上涨概率 62.4%", "interpretation": "模型偏多，但优势并不极端。这说明机器学习模块给出了相对积极的短线概率判断，不过仍需结合市场环境和其他指标共同确认。"},
        ],
        "market_context_points": ["24h 大盘舆情可用于观察市场风险偏好变化。"],
        "risk_points": ["历史数据无法覆盖突发事件冲击。"],
        "sentiment_sections": [
            {"title": "24h 大盘舆情", "subtitle": "示例", "items": ["示例标题 1", "示例标题 2"]},
            {"title": "60d 个股舆情", "subtitle": "示例", "items": ["示例标题 4"]},
        ],
        "charts": {
            "price_svg": "",
            "volume_svg": "",
            "compare_svg": "",
        },
        "ai_summary": "示例 AI 摘要会在这里展示。正式接入后，这里会基于规则分析结果、技术指标、机器学习概率输出以及标题级舆情线索，自动生成一段更完整的自然语言总结。该总结会重点解释当前趋势判断形成的依据，包括哪些模块偏多、哪些模块提示风险、哪些市场背景值得继续跟踪，并在措辞上保持审慎，避免把标题信息当作已证实事实。同时，它也会强调这类报告更适合作为辅助分析材料，帮助使用者更快理解结构化结果，而不是替代独立研究和实际交易决策。",
        "llm_meta": {
            "status": "preview",
            "debug": {},
            "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None},
            "model": "preview",
            "enable_web_search": False,
        },
    }
INDEX_NAME_MAP = {
    "sh000001": "上证指数",
    "sz399001": "深证成指",
    "sz399006": "创业板指",
}
