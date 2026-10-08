from datetime import datetime, timedelta

import pandas as pd

from core.config import MARKET_INDEX_CACHE_DIR
from data_sources.akshare_provider import get_index_history, get_index_intraday, get_index_realtime_snapshots


INDEX_CONFIG = [
    {
        "key": "sh000001",
        "name": "上证指数",
    },
    {
        "key": "sz399001",
        "name": "深证成指",
    },
    {
        "key": "sz399006",
        "name": "创业板指",
    },
]

INDEX_CACHE_FILES = {
    "sh000001": MARKET_INDEX_CACHE_DIR / "sh000001.csv",
    "sz399001": MARKET_INDEX_CACHE_DIR / "sz399001.csv",
    "sz399006": MARKET_INDEX_CACHE_DIR / "sz399006.csv",
}


def _normalize_index_df(df):
    if df is None or df.empty:
        raise ValueError("未获取到指数数据")

    if "trade_date" in df.columns and "date" in df.columns:
        df = df.drop(columns=["date"]).copy()

    rename_map = {
        "trade_date": "date",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "vol": "volume",
        "amount": "amount",
        "pct_chg": "pct_change",
        "change": "change_amount",
    }
    df = df.rename(columns={col: rename_map[col] for col in df.columns if col in rename_map}).copy()

    if "date" not in df.columns or "close" not in df.columns:
        raise ValueError(f"指数数据字段异常: {list(df.columns)}")

    df["date"] = pd.to_datetime(df["date"])
    for col in ["open", "high", "low", "close", "volume", "amount", "pct_change", "change_amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("date").dropna(subset=["close"]).reset_index(drop=True)
    if df.empty:
        raise ValueError("指数数据为空")

    if "change_amount" not in df.columns:
        df["change_amount"] = df["close"].diff()
    if "pct_change" not in df.columns:
        df["pct_change"] = df["close"].pct_change() * 100

    return df


def _save_index_cache(index_key, df):
    MARKET_INDEX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(INDEX_CACHE_FILES[index_key], index=False, encoding="utf-8-sig")


def _load_index_cache(index_key):
    cache_file = INDEX_CACHE_FILES[index_key]
    if not cache_file.exists():
        return None, None

    df = pd.read_csv(cache_file)
    if df.empty:
        return None, None
    updated_at = datetime.fromtimestamp(cache_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    return df, updated_at


def _fetch_single_index(config, start_date, end_date):
    try:
        df = get_index_history(config["key"], start_date, end_date)
        normalized_df = _normalize_index_df(df)
        _save_index_cache(config["key"], normalized_df)
        return normalized_df, False, None
    except Exception as exc:
        cached_df, cache_updated_at = _load_index_cache(config["key"])
        if cached_df is not None:
            return _normalize_index_df(cached_df), True, cache_updated_at
        raise exc


def _merge_realtime_snapshot(chart_df, snapshot):
    """Overlay realtime quote onto historical chart data."""
    if snapshot is None or snapshot.empty:
        return chart_df

    latest_price = snapshot.get("latest_price")
    if latest_price is None or pd.isna(latest_price):
        return chart_df

    merged_df = chart_df.copy()
    today = pd.Timestamp(datetime.now().date())
    latest_row = {
        "date": today,
        "open": float(latest_price),
        "high": float(latest_price),
        "low": float(latest_price),
        "close": float(latest_price),
        "volume": snapshot.get("volume"),
        "amount": snapshot.get("amount"),
        "pct_change": snapshot.get("change_percent"),
        "change_amount": snapshot.get("change_amount"),
    }

    if not merged_df.empty and merged_df.iloc[-1]["date"].normalize() == today:
        for key, value in latest_row.items():
            merged_df.at[merged_df.index[-1], key] = value
    elif merged_df.empty:
        merged_df = pd.DataFrame([latest_row])
    else:
        latest_df = pd.DataFrame([latest_row], columns=merged_df.columns)
        merged_df = pd.concat([merged_df, latest_df], ignore_index=True)

    return _normalize_index_df(merged_df)


def _resample_weekly_index_df(df):
    if df is None or df.empty:
        raise ValueError("未获取到指数数据")

    weekly_df = df.copy().set_index("date")
    weekly_df = weekly_df.resample("W-FRI").agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "amount": "sum",
        }
    )
    weekly_df = weekly_df.dropna(subset=["close"]).reset_index()
    weekly_df["change_amount"] = weekly_df["close"].diff()
    weekly_df["pct_change"] = weekly_df["close"].pct_change() * 100
    return _normalize_index_df(weekly_df)


def get_market_index_data(days=90, k_type="day"):
    days = max(1, min(int(days), 366))
    k_type = "week" if str(k_type).strip().lower() == "week" else "day"
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=days)
    end_date = end_dt.strftime("%Y%m%d")
    start_date = start_dt.strftime("%Y%m%d")

    indices = []
    used_cache = False
    cache_updated_times = []
    realtime_map = {}

    try:
        realtime_df = get_index_realtime_snapshots([config["key"] for config in INDEX_CONFIG])
        realtime_map = {
            row["key"]: row
            for _, row in realtime_df.iterrows()
            if row.get("key")
        }
    except Exception:
        realtime_map = {}

    for config in INDEX_CONFIG:
        if days == 1 and k_type == "day":
            index_used_cache = False
            cache_updated_at = None
            try:
                intraday_df = get_index_intraday(config["key"])
                chart_df = _normalize_index_df(intraday_df)
                chart_df = _merge_realtime_snapshot(chart_df, realtime_map.get(config["key"]))
            except Exception:
                df, index_used_cache, cache_updated_at = _fetch_single_index(config, start_date, end_date)
                chart_df = df[df["date"] >= pd.Timestamp(start_dt.date())].copy()
                if chart_df.empty:
                    chart_df = df.copy()
                chart_df = _merge_realtime_snapshot(chart_df, realtime_map.get(config["key"]))
        else:
            df, index_used_cache, cache_updated_at = _fetch_single_index(config, start_date, end_date)
            chart_df = df[df["date"] >= pd.Timestamp(start_dt.date())].copy()
            if chart_df.empty:
                chart_df = df.copy()
            chart_df = _merge_realtime_snapshot(chart_df, realtime_map.get(config["key"]))
            if k_type == "week":
                chart_df = _resample_weekly_index_df(chart_df)

        used_cache = used_cache or index_used_cache
        if cache_updated_at:
            cache_updated_times.append(cache_updated_at)

        latest = chart_df.iloc[-1]
        previous = chart_df.iloc[-2] if len(chart_df) > 1 else latest
        change_amount = latest.get("change_amount")
        if pd.isna(change_amount):
            change_amount = latest["close"] - previous["close"]

        pct_change = latest.get("pct_change")
        if pd.isna(pct_change):
            pct_change = 0 if previous["close"] == 0 else (latest["close"] - previous["close"]) / previous["close"] * 100

        indices.append(
            {
                "key": config["key"],
                "name": config["name"],
                "latest_close": round(float(latest["close"]), 2),
                "change_amount": round(float(change_amount), 2),
                "change_percent": round(float(pct_change), 2),
                "series": [
                    {
                        "date": row["date"].strftime("%Y-%m-%d"),
                        "time_label": row["date"].strftime("%H:%M") if days == 1 and k_type == "day" else row["date"].strftime("%Y-%m-%d"),
                        "open": round(float(row["open"]), 2) if pd.notna(row.get("open")) else round(float(row["close"]), 2),
                        "high": round(float(row["high"]), 2) if pd.notna(row.get("high")) else round(float(row["close"]), 2),
                        "low": round(float(row["low"]), 2) if pd.notna(row.get("low")) else round(float(row["close"]), 2),
                        "close": round(float(row["close"]), 2),
                        "volume": round(float(row["volume"]), 0) if pd.notna(row.get("volume")) else None,
                        "amount": round(float(row["amount"]), 0) if pd.notna(row.get("amount")) else None,
                    }
                    for _, row in chart_df.iterrows()
                ],
            }
        )

    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not realtime_map and used_cache and cache_updated_times:
        updated_at = min(cache_updated_times)
    return {
        "updated_at": updated_at,
        "is_cached": used_cache,
        "has_realtime": bool(realtime_map),
        "range_days": days,
        "k_type": k_type,
        "default_index": INDEX_CONFIG[0]["key"],
        "indices": indices,
    }
