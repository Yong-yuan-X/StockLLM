import glob
import logging
import os
import time
from datetime import datetime, timedelta

import pandas as pd

from core.config import STOCK_HISTORY_CACHE_DIR
from data_sources.akshare_provider import get_stock_history, get_stock_intraday
from data_sources.market_index import INDEX_CONFIG, INDEX_CACHE_FILES, get_market_index_data
from process import (
    adx_case,
    arima_case,
    bollinger_bands_case,
    linear_regression_case,
    ma_case,
    macd_case,
    random_forest_case,
    rsi_case,
    trend_case,
    volatility_classification_case,
    xgboost_case,
)


AVAILABLE_CASES = {
    "ma": {"label": "MA 均线结构", "runner": ma_case.run_case},
    "rsi": {"label": "RSI 强弱指标", "runner": rsi_case.run_case},
    "macd": {"label": "MACD 动量指标", "runner": macd_case.run_case},
    "trend": {"label": "趋势判断", "runner": trend_case.run_case},
    "bollinger_bands": {"label": "Bollinger Bands 布林带", "runner": bollinger_bands_case.run_case},
    "adx": {"label": "ADX 趋势强度指标", "runner": adx_case.run_case},
    "arima": {"label": "ARIMA 时序预测", "runner": arima_case.run_case},
    "volatility_classification": {"label": "波动率分类", "runner": volatility_classification_case.run_case},
    "random_forest": {"label": "Random Forest 分类", "runner": random_forest_case.run_case},
    "xgboost": {"label": "XGBoost 分类", "runner": xgboost_case.run_case},
    "linear_regression": {"label": "线性回归预测", "runner": linear_regression_case.run_case},
}
DEFAULT_CASE_ORDER = [
    "ma",
    "rsi",
    "macd",
    "arima",
    "xgboost",
    "trend",
    "bollinger_bands",
    "adx",
    "volatility_classification",
    "random_forest",
    "linear_regression",
]

CASE_CATEGORY_MAP = {
    "ma": "technical",
    "rsi": "technical",
    "macd": "technical",
    "trend": "technical",
    "bollinger_bands": "technical",
    "adx": "technical",
    "volatility_classification": "technical",
    "arima": "time_series",
    "linear_regression": "time_series",
    "random_forest": "machine_learning",
    "xgboost": "machine_learning",
}

RISK_PREFERENCE_WEIGHTS = {
    "conservative": {"technical": 0.5, "time_series": 0.3, "machine_learning": 0.2},
    "balanced": {"technical": 0.33, "time_series": 0.33, "machine_learning": 0.34},
    "aggressive": {"technical": 0.2, "time_series": 0.3, "machine_learning": 0.5},
}

THETA_BULLISH = 0.6
THETA_BEARISH = 0.4


logger = logging.getLogger(__name__)


def read_latest_stock_csv(stock_code, data_dir=None):
    resolved_dir = str(data_dir or STOCK_HISTORY_CACHE_DIR)
    pattern = os.path.join(resolved_dir, f"{stock_code}_daily_*.csv")
    csv_files = glob.glob(pattern)
    if not csv_files:
        return None
    latest_file = max(csv_files, key=os.path.getmtime)
    return latest_file


def load_latest_stock_dataframe(stock_code, data_dir=None):
    index_cache_file = INDEX_CACHE_FILES.get(str(stock_code or "").strip())
    if index_cache_file and index_cache_file.exists():
        df = pd.read_csv(index_cache_file, encoding="utf-8-sig")
        rename_map = {
            "date": "trade_date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "pct_change": "pct_chg",
            "change_amount": "change",
            "volume": "volume",
            "amount": "amount",
        }
        working_df = df.rename(columns={column: rename_map[column] for column in df.columns if column in rename_map}).copy()
        if "trade_date" not in working_df.columns or "close" not in working_df.columns:
            raise ValueError("历史数据字段不完整，无法执行指标分析")

        working_df["trade_date"] = pd.to_datetime(working_df["trade_date"], errors="coerce")
        for column in ["open", "high", "low", "close", "change", "pct_chg", "volume", "amount"]:
            if column in working_df.columns:
                working_df[column] = pd.to_numeric(working_df[column], errors="coerce")
        working_df["preclose"] = working_df["close"].shift(1)
        working_df = working_df.dropna(subset=["trade_date", "close"]).sort_values("trade_date").reset_index(drop=True)
        return working_df, str(index_cache_file)

    latest_file = read_latest_stock_csv(stock_code, data_dir=data_dir)
    if not latest_file:
        return None, None

    df = pd.read_csv(latest_file, encoding="utf-8-sig")
    rename_map = {
        "日期": "trade_date",
        "开盘": "open",
        "最高": "high",
        "最低": "low",
        "收盘": "close",
        "昨收": "preclose",
        "涨跌额": "change",
        "涨跌幅": "pct_chg",
        "成交量": "volume",
        "成交额": "amount",
    }
    working_df = df.rename(columns={column: rename_map[column] for column in df.columns if column in rename_map}).copy()
    if "trade_date" not in working_df.columns or "close" not in working_df.columns:
        raise ValueError("历史数据字段不完整，无法执行指标分析")

    working_df["trade_date"] = pd.to_datetime(working_df["trade_date"], errors="coerce")
    for column in ["open", "high", "low", "close", "preclose", "change", "pct_chg", "volume", "amount"]:
        if column in working_df.columns:
            working_df[column] = pd.to_numeric(working_df[column], errors="coerce")

    working_df = working_df.dropna(subset=["trade_date", "close"]).sort_values("trade_date").reset_index(drop=True)
    return working_df, latest_file


def ensure_stock_history_dataframe(stock_code, auto_update=True, data_dir=None):
    stock_df, file_path = load_latest_stock_dataframe(stock_code, data_dir=data_dir)
    if (stock_df is None or stock_df.empty) and auto_update:
        update_stock_history_csv(stock_code, data_dir=data_dir)
        stock_df, file_path = load_latest_stock_dataframe(stock_code, data_dir=data_dir)

    if stock_df is None or stock_df.empty:
        raise FileNotFoundError(f"未找到{stock_code}的历史数据")
    return stock_df, file_path


def update_stock_history_csv(stock_code, data_dir=None):
    resolved_dir = STOCK_HISTORY_CACHE_DIR if data_dir is None else data_dir
    yesterday = datetime.now() - timedelta(days=1)
    end_date = yesterday.strftime("%Y%m%d")
    start_date = (yesterday - timedelta(days=365 * 3)).strftime("%Y%m%d")

    stock_df = get_stock_history(
        stock_code=stock_code,
        start_date=start_date,
        end_date=end_date,
        adjust="qfq",
    )

    export_df = stock_df.rename(
        columns={
            "trade_date": "日期",
            "open": "开盘",
            "high": "最高",
            "low": "最低",
            "close": "收盘",
            "preclose": "昨收",
            "change": "涨跌额",
            "pct_chg": "涨跌幅",
            "volume": "成交量",
            "amount": "成交额",
        }
    )

    resolved_dir = str(resolved_dir)
    os.makedirs(resolved_dir, exist_ok=True)
    csv_filename = f"{resolved_dir}/{stock_code}_daily_{start_date}_{end_date}.csv"
    export_df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
    return {
        "stock_code": stock_code,
        "date_range": f"{start_date} 至 {end_date}",
        "file_path": csv_filename,
        "data_count": len(stock_df),
        "data_source": stock_df.attrs.get("source", "unknown"),
        "data_source_label": {
            "eastmoney": "东方财富",
            "tencent": "腾讯",
            "unknown": "未知",
        }.get(stock_df.attrs.get("source", "unknown"), stock_df.attrs.get("source", "unknown")),
    }


def build_stock_chart_payload(stock_code, stock_name="", days=90):
    days = max(1, min(int(days or 90), 365))
    if days == 1:
        stock_df = get_stock_intraday(stock_code)
        file_path = None
        price_df = stock_df.copy()
        volume_df = stock_df.copy()
    else:
        stock_df, file_path = ensure_stock_history_dataframe(stock_code, auto_update=True)
        price_df = stock_df.tail(min(days, len(stock_df))).copy()
        volume_df = stock_df.tail(min(days, len(stock_df))).copy()
    latest_row = price_df.iloc[-1]
    previous_row = price_df.iloc[-2] if len(price_df) > 1 else latest_row

    market_series = []
    market_name = "上证指数"
    market_return = None
    stock_return = None
    excess_return = None
    try:
        market_data = get_market_index_data(days=days, k_type="day")
        sh_index = next((item for item in market_data.get("indices", []) if item.get("key") == "sh000001"), None)
        if sh_index:
            market_name = sh_index.get("name") or market_name
            market_series = sh_index.get("series") or []
            if market_series:
                market_return = round(
                    (float(market_series[-1]["close"]) - float(market_series[0]["close"])) / float(market_series[0]["close"]) * 100,
                    2,
                )
    except Exception:
        market_series = []

    if not price_df.empty:
        stock_return = round((float(price_df.iloc[-1]["close"]) - float(price_df.iloc[0]["close"])) / float(price_df.iloc[0]["close"]) * 100, 2)
    if stock_return is not None and market_return is not None:
        excess_return = round(stock_return - market_return, 2)

    return {
        "stock_code": stock_code,
        "stock_name": stock_name,
        "source_file": file_path,
        "range_days": days,
        "latest_close": round(float(latest_row["close"]), 2),
        "change_amount": round(float(latest_row["close"] - previous_row["close"]), 2),
        "change_percent": round(float((latest_row["close"] - previous_row["close"]) / previous_row["close"] * 100), 2) if float(previous_row["close"]) else 0.0,
        "price_series": [
            {
                "date": row["trade_date"].strftime("%Y-%m-%d"),
                "time_label": row["trade_date"].strftime("%H:%M") if days == 1 else row["trade_date"].strftime("%Y-%m-%d"),
                "open": round(float(row["open"]), 2) if pd.notna(row.get("open")) else None,
                "high": round(float(row["high"]), 2) if pd.notna(row.get("high")) else None,
                "low": round(float(row["low"]), 2) if pd.notna(row.get("low")) else None,
                "close": round(float(row["close"]), 2),
            }
            for _, row in price_df.iterrows()
        ],
        "volume_series": [
            {
                "date": row["trade_date"].strftime("%Y-%m-%d"),
                "time_label": row["trade_date"].strftime("%H:%M") if days == 1 else row["trade_date"].strftime("%Y-%m-%d"),
                "volume": float(row["volume"]) if pd.notna(row.get("volume")) else None,
                "amount": float(row["amount"]) if pd.notna(row.get("amount")) else None,
                "open": round(float(row["open"]), 2) if pd.notna(row.get("open")) else None,
                "close": round(float(row["close"]), 2),
            }
            for _, row in volume_df.iterrows()
        ],
        "market_compare": {
            "market_name": market_name,
            "stock_return": stock_return,
            "market_return": market_return,
            "excess_return": excess_return,
            "stock_series": [
                {
                    "date": row["trade_date"].strftime("%Y-%m-%d"),
                    "time_label": row["trade_date"].strftime("%H:%M") if days == 1 else row["trade_date"].strftime("%Y-%m-%d"),
                    "close": round(float(row["close"]), 2),
                }
                for _, row in price_df.iterrows()
            ],
            "market_series": market_series,
        },
    }


def normalize_selected_cases(selected_cases=None):
    if not selected_cases:
        return DEFAULT_CASE_ORDER[:]

    normalized = []
    for case_name in selected_cases:
        case_key = str(case_name or "").strip().lower()
        if case_key in AVAILABLE_CASES and case_key not in normalized:
            normalized.append(case_key)
    return normalized or DEFAULT_CASE_ORDER[:]


def _load_market_index_analysis_dataframe(index_key):
    index_code = str(index_key or "").strip()
    config = next((item for item in INDEX_CONFIG if item["key"] == index_code), None)
    if not config:
        raise ValueError("不支持的指数代码")

    get_market_index_data(days=366, k_type="day")
    cache_file = INDEX_CACHE_FILES.get(index_code)
    if cache_file is None or not cache_file.exists():
        raise FileNotFoundError(f"未找到 {index_code} 的指数历史数据")

    df = pd.read_csv(cache_file, encoding="utf-8-sig")
    rename_map = {
        "date": "trade_date",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "pct_change": "pct_chg",
        "change_amount": "change",
        "volume": "volume",
        "amount": "amount",
    }
    working_df = df.rename(columns=rename_map).copy()
    if "trade_date" not in working_df.columns or "close" not in working_df.columns:
        raise ValueError("指数历史数据字段不完整，无法执行分析")

    working_df["trade_date"] = pd.to_datetime(working_df["trade_date"], errors="coerce")
    for column in ["open", "high", "low", "close", "change", "pct_chg", "volume", "amount"]:
        if column in working_df.columns:
            working_df[column] = pd.to_numeric(working_df[column], errors="coerce")
    working_df["preclose"] = working_df["close"].shift(1)
    working_df = working_df.dropna(subset=["trade_date", "close"]).sort_values("trade_date").reset_index(drop=True)
    if working_df.empty:
        raise FileNotFoundError(f"未找到 {index_code} 的指数历史数据")

    return working_df, str(cache_file), config["name"]


def normalize_risk_preference(risk_preference=None):
    raw_value = str(risk_preference or "").strip().lower()
    if raw_value in RISK_PREFERENCE_WEIGHTS:
        return raw_value

    level_map = {
        "1": "aggressive",
        "2": "aggressive",
        "3": "balanced",
        "4": "conservative",
        "5": "conservative",
        "激进": "aggressive",
        "偏激进": "aggressive",
        "平和": "balanced",
        "平衡": "balanced",
        "偏保守": "conservative",
        "保守": "conservative",
    }
    return level_map.get(raw_value, "balanced")


def _signal_to_probability(signal):
    normalized_signal = str(signal or "").strip().lower()
    if normalized_signal == "bullish":
        return 1.0
    if normalized_signal == "bearish":
        return 0.0
    return 0.5


def _build_weighted_fusion(results, risk_preference):
    normalized_preference = normalize_risk_preference(risk_preference)
    category_scores = {
        "technical": [],
        "time_series": [],
        "machine_learning": [],
    }

    for item in results:
        category = CASE_CATEGORY_MAP.get(item.get("case"))
        if not category:
            continue
        category_scores[category].append(_signal_to_probability(item.get("signal")))

    normalized_category_scores = {}
    for category, values in category_scores.items():
        normalized_category_scores[category] = round(sum(values) / len(values), 4) if values else 0.5

    weights = RISK_PREFERENCE_WEIGHTS[normalized_preference]
    fusion_score = round(
        normalized_category_scores["technical"] * weights["technical"]
        + normalized_category_scores["time_series"] * weights["time_series"]
        + normalized_category_scores["machine_learning"] * weights["machine_learning"],
        4,
    )
    return normalized_preference, weights, normalized_category_scores, fusion_score


def _build_overall_signal(results, risk_preference="balanced"):
    total_score = sum(item["score"] for item in results)
    bullish_count = len([item for item in results if item["signal"] == "bullish"])
    bearish_count = len([item for item in results if item["signal"] == "bearish"])
    neutral_count = len([item for item in results if item["signal"] == "neutral"])
    normalized_preference, weights, category_scores, fusion_score = _build_weighted_fusion(results, risk_preference)

    if fusion_score > THETA_BULLISH:
        overall_signal = "bullish"
    elif fusion_score < THETA_BEARISH:
        overall_signal = "bearish"
    else:
        overall_signal = "neutral"

    return {
        "overall_signal": overall_signal,
        "total_score": total_score,
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "neutral_count": neutral_count,
        "risk_preference_mode": normalized_preference,
        "weighted_fusion_score": fusion_score,
        "theta_bullish": THETA_BULLISH,
        "theta_bearish": THETA_BEARISH,
        "category_scores": category_scores,
        "category_weights": weights,
    }


def predict_stock_movement(stock_code, days, selected_cases=None, risk_preference="balanced"):
    started_at = time.perf_counter()
    days = int(days or 0)
    if days < 1 or days > 365:
        raise ValueError("预测天数只能在1到365天之间")

    load_started_at = time.perf_counter()
    stock_df, file_path = ensure_stock_history_dataframe(stock_code, auto_update=False)
    load_elapsed = round(time.perf_counter() - load_started_at, 3)

    case_keys = normalize_selected_cases(selected_cases)
    results = []
    case_timings = []
    for case_key in case_keys:
        runner = AVAILABLE_CASES[case_key]["runner"]
        case_started_at = time.perf_counter()
        results.append(runner(stock_df, predict_days=days))
        case_timings.append(
            {
                "case": case_key,
                "label": AVAILABLE_CASES[case_key]["label"],
                "elapsed_seconds": round(time.perf_counter() - case_started_at, 3),
            }
        )

    latest_row = stock_df.iloc[-1]
    normalized_preference = normalize_risk_preference(risk_preference)
    aggregate_started_at = time.perf_counter()
    aggregate = _build_overall_signal(results, risk_preference=normalized_preference)
    aggregate_elapsed = round(time.perf_counter() - aggregate_started_at, 3)
    total_elapsed = round(time.perf_counter() - started_at, 3)
    timing_breakdown = {
        "load_history_seconds": load_elapsed,
        "cases_total_seconds": round(sum(item["elapsed_seconds"] for item in case_timings), 3),
        "aggregate_seconds": aggregate_elapsed,
        "total_seconds": total_elapsed,
        "case_timings": case_timings,
    }
    logger.info(
        "股票分析阶段耗时 stock=%s total=%.3fs load_history=%.3fs cases_total=%.3fs aggregate=%.3fs per_case=%s",
        stock_code,
        total_elapsed,
        load_elapsed,
        timing_breakdown["cases_total_seconds"],
        aggregate_elapsed,
        ", ".join(f"{item['case']}={item['elapsed_seconds']:.3f}s" for item in case_timings) or "none",
    )

    return {
        "stock_code": stock_code,
        "predict_days": days,
        "analysis_mode": "rule_based",
        "risk_preference_mode": normalized_preference,
        "selected_cases": case_keys,
        "selected_case_labels": [AVAILABLE_CASES[case_key]["label"] for case_key in case_keys],
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_file": file_path,
        "data_summary": {
            "rows": int(len(stock_df)),
            "date_start": stock_df.iloc[0]["trade_date"].strftime("%Y-%m-%d"),
            "date_end": latest_row["trade_date"].strftime("%Y-%m-%d"),
            "latest_close": round(float(latest_row["close"]), 2),
            "latest_pct_chg": round(float(latest_row["pct_chg"]), 2) if pd.notna(latest_row.get("pct_chg")) else None,
        },
        "analysis_results": results,
        "aggregate": aggregate,
        "timing_breakdown": timing_breakdown,
    }


def predict_market_index_movement(index_key, days, selected_cases=None, risk_preference="balanced"):
    started_at = time.perf_counter()
    days = int(days or 0)
    if days < 1 or days > 365:
        raise ValueError("预测天数只能在1到365天之间")

    load_started_at = time.perf_counter()
    index_df, file_path, index_name = _load_market_index_analysis_dataframe(index_key)
    load_elapsed = round(time.perf_counter() - load_started_at, 3)
    case_keys = normalize_selected_cases(selected_cases)
    results = []
    case_timings = []
    for case_key in case_keys:
        runner = AVAILABLE_CASES[case_key]["runner"]
        case_started_at = time.perf_counter()
        results.append(runner(index_df, predict_days=days))
        case_timings.append(
            {
                "case": case_key,
                "label": AVAILABLE_CASES[case_key]["label"],
                "elapsed_seconds": round(time.perf_counter() - case_started_at, 3),
            }
        )

    latest_row = index_df.iloc[-1]
    normalized_preference = normalize_risk_preference(risk_preference)
    aggregate_started_at = time.perf_counter()
    aggregate = _build_overall_signal(results, risk_preference=normalized_preference)
    aggregate_elapsed = round(time.perf_counter() - aggregate_started_at, 3)
    total_elapsed = round(time.perf_counter() - started_at, 3)
    timing_breakdown = {
        "load_history_seconds": load_elapsed,
        "cases_total_seconds": round(sum(item["elapsed_seconds"] for item in case_timings), 3),
        "aggregate_seconds": aggregate_elapsed,
        "total_seconds": total_elapsed,
        "case_timings": case_timings,
    }
    logger.info(
        "大盘分析阶段耗时 index=%s total=%.3fs load_history=%.3fs cases_total=%.3fs aggregate=%.3fs per_case=%s",
        index_key,
        total_elapsed,
        load_elapsed,
        timing_breakdown["cases_total_seconds"],
        aggregate_elapsed,
        ", ".join(f"{item['case']}={item['elapsed_seconds']:.3f}s" for item in case_timings) or "none",
    )

    return {
        "stock_code": index_key,
        "stock_name": index_name,
        "predict_days": days,
        "analysis_mode": "market_index_rule_based",
        "risk_preference_mode": normalized_preference,
        "selected_cases": case_keys,
        "selected_case_labels": [AVAILABLE_CASES[case_key]["label"] for case_key in case_keys],
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_file": file_path,
        "data_summary": {
            "rows": int(len(index_df)),
            "date_start": index_df.iloc[0]["trade_date"].strftime("%Y-%m-%d"),
            "date_end": latest_row["trade_date"].strftime("%Y-%m-%d"),
            "latest_close": round(float(latest_row["close"]), 2),
            "latest_pct_chg": round(float(latest_row["pct_chg"]), 2) if pd.notna(latest_row.get("pct_chg")) else None,
        },
        "analysis_results": results,
        "aggregate": aggregate,
        "timing_breakdown": timing_breakdown,
    }
