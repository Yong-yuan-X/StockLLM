from datetime import datetime
from pathlib import Path
import time

import pandas as pd

from data_sources.akshare_provider import (
    get_full_market_snapshots,
    get_full_market_snapshots_fallback,
    get_full_market_snapshots_sina,
    get_industry_constituents,
    get_industry_directory,
    get_market_rankings_sina,
    get_stock_directory_snapshot,
    get_stock_snapshots,
)
from core.config import (
    DEFAULT_SECTORS,
    SECTOR_CACHE_FILE,
    SECTOR_STOCK_CACHE_DIR,
    STOCK_DIRECTORY_CACHE_FILE,
    STOCK_RANKING_CACHE_FILE,
)
from core.services.user_stock_service import list_user_stocks


def _safe_cache_name(value):
    return "".join(ch if ch.isalnum() else "_" for ch in value).strip("_") or "default"


def _save_cache_df(df, file_path):
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def _load_cache_df(file_path):
    path = Path(file_path)
    if not path.exists():
        return None

    df = pd.read_csv(path, dtype=str)
    return df if not df.empty else None


def _cache_updated_at(file_path):
    path = Path(file_path)
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def _normalize_sector_list_df(df):
    if df is None or df.empty:
        raise ValueError("未获取到板块列表")

    rename_map = {
        "板块名称": "sector_name",
        "名称": "sector_name",
        "name": "sector_name",
        "板块代码": "sector_code",
        "代码": "sector_code",
        "code": "sector_code",
    }
    df = df.rename(columns={col: rename_map[col] for col in df.columns if col in rename_map}).copy()

    if "sector_name" not in df.columns:
        raise ValueError(f"板块列表字段异常: {list(df.columns)}")

    if "sector_code" not in df.columns:
        df["sector_code"] = ""

    df["sector_name"] = df["sector_name"].astype(str).str.strip()
    df["sector_code"] = df["sector_code"].astype(str).str.strip()
    df = df[df["sector_name"] != ""].drop_duplicates(subset=["sector_name"]).reset_index(drop=True)
    if df.empty:
        raise ValueError("板块列表为空")

    return df[["sector_name", "sector_code"]]


def _normalize_sector_constituents_df(df):
    if df is None or df.empty:
        raise ValueError("未获取到板块成分股")

    rename_map = {
        "代码": "code",
        "名称": "name",
        "industry": "industry",
        "所属行业": "industry",
        "market": "market",
        "市场": "market",
        "最新价": "latest_price",
        "涨跌幅": "change_percent",
        "涨跌额": "change_amount",
        "换手率": "turnover_rate",
        "成交量": "volume",
        "成交额": "amount",
        "市盈率-动态": "pe_ratio",
        "市净率": "pb_ratio",
    }
    df = df.rename(columns={col: rename_map[col] for col in df.columns if col in rename_map}).copy()

    for required in ["code", "name"]:
        if required not in df.columns:
            raise ValueError(f"板块成分股字段异常: {list(df.columns)}")

    for col in ["industry", "market"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).str.strip()

    numeric_columns = [
        "latest_price",
        "change_percent",
        "change_amount",
        "turnover_rate",
        "volume",
        "amount",
        "pe_ratio",
        "pb_ratio",
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce") if col in df.columns else None

    df["code"] = df["code"].astype(str).str.strip()
    df["name"] = df["name"].astype(str).str.strip()
    df = df[(df["code"] != "") & (df["name"] != "")].reset_index(drop=True)
    if df.empty:
        raise ValueError("板块成分股为空")

    return df[
        [
            "code",
            "name",
            "industry",
            "market",
            "latest_price",
            "change_percent",
            "change_amount",
            "turnover_rate",
            "volume",
            "amount",
            "pe_ratio",
            "pb_ratio",
        ]
    ]


def _normalize_stock_directory_df(df):
    if df is None or df.empty:
        raise ValueError("未获取到个股列表")

    rename_map = {
        "代码": "code",
        "证券代码": "code",
        "stock_code": "code",
        "symbol": "code",
        "名称": "name",
        "证券简称": "name",
        "stock_name": "name",
        "industry": "industry",
        "所属行业": "industry",
        "market": "market",
        "市场": "market",
        "最新价": "latest_price",
        "涨跌幅": "change_percent",
        "涨跌额": "change_amount",
        "成交量": "volume",
        "成交额": "amount",
        "换手率": "turnover_rate",
        "市盈率-动态": "pe_ratio",
        "市净率": "pb_ratio",
        "总市值": "market_value",
    }
    df = df.rename(columns={col: rename_map[col] for col in df.columns if col in rename_map}).copy()

    if "code" not in df.columns or "name" not in df.columns:
        raise ValueError(f"个股列表字段异常: {list(df.columns)}")

    for col in ["industry", "market"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).str.strip()

    numeric_columns = [
        "latest_price",
        "change_percent",
        "change_amount",
        "volume",
        "amount",
        "turnover_rate",
        "pe_ratio",
        "pb_ratio",
        "market_value",
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce") if col in df.columns else None

    df["code"] = df["code"].astype(str).str.strip()
    df["name"] = df["name"].astype(str).str.strip()
    df = df[(df["code"] != "") & (df["name"] != "")].drop_duplicates(subset=["code"]).reset_index(drop=True)
    if df.empty:
        raise ValueError("个股列表为空")

    return df[
        [
            "code",
            "name",
            "industry",
            "market",
            "latest_price",
            "change_percent",
            "change_amount",
            "volume",
            "amount",
            "turnover_rate",
            "pe_ratio",
            "pb_ratio",
            "market_value",
        ]
    ]


def _format_numeric(value, digits=2):
    if value is None or pd.isna(value):
        return None
    return round(float(value), digits)


def _paginate_dataframe(df, page=1, page_size=20):
    total = len(df)
    page_size = max(1, min(int(page_size), 100))
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(int(page), total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    return df.iloc[start:end].copy(), total, total_pages, page, page_size


def _split_keywords(keyword):
    raw = str(keyword or "").strip()
    if not raw:
        return []

    normalized = raw
    for separator in ["\n", "\t", "，", ",", "、", ";", "；", "|"]:
        normalized = normalized.replace(separator, " ")

    deduped = []
    for item in [part.strip().lower() for part in normalized.split(" ") if part.strip()]:
        if item not in deduped:
            deduped.append(item)
    return deduped


def fetch_sector_options():
    error_messages = []
    try:
        df = _normalize_sector_list_df(get_industry_directory())
        _save_cache_df(df, SECTOR_CACHE_FILE)
        source = "live"
    except Exception as exc:
        error_messages.append(str(exc))
        df = _load_cache_df(SECTOR_CACHE_FILE)
        if df is None:
            df = pd.DataFrame({"sector_name": DEFAULT_SECTORS, "sector_code": [""] * len(DEFAULT_SECTORS)})
            source = "fallback"
        else:
            df = _normalize_sector_list_df(df)
            source = "cache"

    sector_records = [{"sector_name": row["sector_name"], "sector_code": row["sector_code"]} for _, row in df.iterrows()]
    recommended = []
    for name in DEFAULT_SECTORS:
        matched = next((item for item in sector_records if item["sector_name"] == name), None)
        if matched and all(existing["sector_name"] != name for existing in recommended):
            recommended.append(matched)
    for item in sector_records:
        if all(existing["sector_name"] != item["sector_name"] for existing in recommended):
            recommended.append(item)
        if len(recommended) >= 5:
            break

    return {
        "recommended": recommended[:5],
        "all_sectors": sector_records,
        "updated_at": _cache_updated_at(SECTOR_CACHE_FILE) if source != "live" else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "warning": "；".join(error_messages) if error_messages else None,
    }


def fetch_sector_constituents(sector_name, sector_code="", keyword="", page=1, page_size=10):
    if not sector_name:
        raise ValueError("请输入板块名称")

    cache_file = SECTOR_STOCK_CACHE_DIR / f"{_safe_cache_name(sector_name)}.csv"
    error_messages = []
    try:
        sector_response = get_industry_constituents(
            sector_name,
            sector_code=sector_code,
            page=page,
            page_size=page_size,
        )
        df = _normalize_sector_constituents_df(sector_response["items"])
        _save_cache_df(df, cache_file)
        source = "live"
    except Exception as exc:
        error_messages.append(str(exc))
        df = _load_cache_df(cache_file)
        if df is None:
            raise RuntimeError("板块成分股获取失败：" + " | ".join(error_messages))
        df = _normalize_sector_constituents_df(df)
        source = "cache"
        sector_response = {
            "sector_code": sector_code,
            "page": page,
            "page_size": page_size,
            "total": len(df),
            "total_pages": max(1, (len(df) + max(1, page_size) - 1) // max(1, page_size)),
        }

    keyword = (keyword or "").strip().lower()
    if keyword:
        df = df[
            df["code"].astype(str).str.lower().str.contains(keyword, na=False)
            | df["name"].astype(str).str.lower().str.contains(keyword, na=False)
        ].reset_index(drop=True)

    if source == "cache" or keyword:
        page_df, total, total_pages, page, page_size = _paginate_dataframe(df, page=page, page_size=page_size)
    else:
        page_df = df
        total = int(sector_response.get("total", len(df)))
        total_pages = int(sector_response.get("total_pages", 1))
        page = int(sector_response.get("page", page))
        page_size = int(sector_response.get("page_size", page_size))

    return {
        "sector_name": sector_name,
        "sector_code": sector_response.get("sector_code", sector_code),
        "items": [
            {
                "code": row["code"],
                "name": row["name"],
                "industry": row.get("industry", ""),
                "market": row.get("market", ""),
                "trade_date": row.get("trade_date"),
                "latest_price": _format_numeric(row.get("latest_price")),
                "change_percent": _format_numeric(row.get("change_percent")),
                "change_amount": _format_numeric(row.get("change_amount")),
                "turnover_rate": _format_numeric(row.get("turnover_rate")),
                "volume": _format_numeric(row.get("volume"), 0),
                "amount": _format_numeric(row.get("amount"), 0),
                "pe_ratio": _format_numeric(row["pe_ratio"]),
                "pb_ratio": _format_numeric(row["pb_ratio"]),
            }
            for _, row in page_df.iterrows()
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
        "updated_at": _cache_updated_at(cache_file) if source != "live" else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "warning": "；".join(error_messages) if error_messages else None,
    }


def fetch_stock_directory(keyword="", page=1, page_size=20):
    error_messages = []
    search_terms = _split_keywords(keyword)
    if not search_terms:
        return {
            "items": [],
            "pagination": {"page": 1, "page_size": page_size, "total": 0, "total_pages": 1},
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "live",
            "warning": "请输入一个或多个股票代码/名称后，再查询最新交易日快照",
        }

    try:
        df = _normalize_stock_directory_df(get_stock_directory_snapshot())
        _save_cache_df(df, STOCK_DIRECTORY_CACHE_FILE)
        source = "live"
    except Exception as primary_exc:
        error_messages.append(f"akshare_stock_directory: {primary_exc}")
        df = _load_cache_df(STOCK_DIRECTORY_CACHE_FILE)
        if df is None:
            raise RuntimeError("个股明细获取失败：" + " | ".join(error_messages))
        df = _normalize_stock_directory_df(df)
        source = "cache"

    match_mask = pd.Series(False, index=df.index)
    for term in search_terms:
        match_mask = match_mask | (
            df["code"].astype(str).str.lower().str.contains(term, na=False)
            | df["name"].astype(str).str.lower().str.contains(term, na=False)
        )
    df = df[match_mask].reset_index(drop=True)

    page_df, total, total_pages, page, page_size = _paginate_dataframe(df, page=page, page_size=page_size)
    snapshot_df = pd.DataFrame()
    if not page_df.empty:
        try:
            snapshot_df = get_stock_snapshots(page_df["code"].tolist())
        except Exception as snapshot_exc:
            error_messages.append(f"snapshot: {snapshot_exc}")

    if not snapshot_df.empty:
        page_df = page_df.merge(snapshot_df, on="code", how="left", suffixes=("", "_snapshot"))

    return {
        "items": [
            {
                "code": row["code"],
                "name": row["name"],
                "industry": row.get("industry", ""),
                "market": row.get("market", ""),
                "trade_date": row.get("trade_date"),
                "latest_price": _format_numeric(row.get("latest_price_snapshot", row.get("latest_price"))),
                "change_percent": _format_numeric(row.get("change_percent_snapshot", row.get("change_percent"))),
                "change_amount": _format_numeric(row.get("change_amount_snapshot", row.get("change_amount"))),
                "turnover_rate": _format_numeric(row.get("turnover_rate_snapshot", row.get("turnover_rate"))),
                "volume": _format_numeric(row.get("volume_snapshot", row.get("volume")), 0),
                "amount": _format_numeric(row.get("amount_snapshot", row.get("amount")), 0),
            }
            for _, row in page_df.iterrows()
        ],
        "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": total_pages},
        "updated_at": _cache_updated_at(STOCK_DIRECTORY_CACHE_FILE) if source != "live" else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "warning": "；".join(error_messages) if error_messages else "当前展示的是新浪实时快照，股票检索列表来自本地股票代码名称表",
    }


def _merge_snapshot_rows(base_df, snapshot_df):
    if snapshot_df is None or snapshot_df.empty:
        return base_df.copy()
    return base_df.merge(snapshot_df, on="code", how="left", suffixes=("", "_snapshot"))


def _format_stock_item(row):
    return {
        "code": row["code"],
        "name": row["name"],
        "industry": row.get("industry", ""),
        "market": row.get("market", ""),
        "trade_date": row.get("trade_date_snapshot", row.get("trade_date")),
        "latest_price": _format_numeric(row.get("latest_price_snapshot", row.get("latest_price"))),
        "change_percent": _format_numeric(row.get("change_percent_snapshot", row.get("change_percent"))),
        "change_amount": _format_numeric(row.get("change_amount_snapshot", row.get("change_amount"))),
        "turnover_rate": _format_numeric(row.get("turnover_rate_snapshot", row.get("turnover_rate"))),
        "volume": _format_numeric(row.get("volume_snapshot", row.get("volume")), 0),
        "amount": _format_numeric(row.get("amount_snapshot", row.get("amount")), 0),
    }


def fetch_stock_rankings(limit=10):
    limit = max(5, min(int(limit or 10), 30))
    gainers = []
    losers = []
    source = None
    warning_messages = []
    source_chain = [
        ("eastmoney", get_full_market_snapshots),
        ("akshare", get_full_market_snapshots_fallback),
    ]

    for index, (source_name, fetcher) in enumerate(source_chain):
        try:
            snapshot_df = _normalize_stock_directory_df(fetcher())
            ranked_df = snapshot_df.dropna(subset=["change_percent"]).sort_values("change_percent", ascending=False).reset_index(drop=True)
            gainers = [_format_stock_item(row) for _, row in ranked_df.head(limit).iterrows()]
            losers = [_format_stock_item(row) for _, row in ranked_df.tail(limit).iloc[::-1].iterrows()]
            _save_cache_df(ranked_df, STOCK_RANKING_CACHE_FILE)
            source = source_name
            break
        except Exception as exc:
            warning_messages.append(f"{source_name}: {exc}")
            if index < len(source_chain) - 1:
                time.sleep(3)

    if not gainers and not losers:
        try:
            time.sleep(3)
            sina_rankings = get_market_rankings_sina(limit)
            gainers = [_format_stock_item(row) for _, row in sina_rankings["gainers"].iterrows()]
            losers = [_format_stock_item(row) for _, row in sina_rankings["losers"].iterrows()]
            cache_df = pd.concat([sina_rankings["gainers"], sina_rankings["losers"]], ignore_index=True).drop_duplicates(subset=["code"])
            _save_cache_df(cache_df, STOCK_RANKING_CACHE_FILE)
            source = "sina"
        except Exception as exc:
            warning_messages.append(f"sina: {exc}")

    if not gainers and not losers:
        cached_df = _load_cache_df(STOCK_RANKING_CACHE_FILE)
        if cached_df is not None:
            snapshot_df = _normalize_stock_directory_df(cached_df)
            ranked_df = snapshot_df.dropna(subset=["change_percent"]).sort_values("change_percent", ascending=False).reset_index(drop=True)
            gainers = [_format_stock_item(row) for _, row in ranked_df.head(limit).iterrows()]
            losers = [_format_stock_item(row) for _, row in ranked_df.tail(limit).iloc[::-1].iterrows()]
            source = "cache"
        else:
            snapshot_df = _normalize_stock_directory_df(get_stock_directory_snapshot())
            ranked_df = snapshot_df.dropna(subset=["change_percent"]).sort_values("change_percent", ascending=False).reset_index(drop=True)
            gainers = [_format_stock_item(row) for _, row in ranked_df.head(limit).iterrows()]
            losers = [_format_stock_item(row) for _, row in ranked_df.tail(limit).iloc[::-1].iterrows()]
            source = "directory_snapshot"
            warning_messages.append("缓存不存在，已退回静态股票目录。")

    return {
        "gainers": gainers,
        "losers": losers,
        "updated_at": _cache_updated_at(STOCK_RANKING_CACHE_FILE) if source == "cache" else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "warning": "；".join(warning_messages) if warning_messages else None,
    }


def fetch_favorite_snapshot(user_id):
    stocks = list_user_stocks(user_id)
    if not stocks:
        return {
            "items": [],
            "summary": {"up_count": 0, "down_count": 0, "flat_count": 0, "total": 0, "total_volume": 0, "total_amount": 0},
            "distribution": [],
            "volume_amount_chart": [],
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "live",
            "warning": "暂无自选股",
        }

    codes = [item["stock_code"] for item in stocks]
    base_df = pd.DataFrame(
        [{"code": item["stock_code"], "name": item["stock_name"], "industry": "", "market": "", "trade_date": None} for item in stocks]
    )
    snapshot_df = get_stock_snapshots(codes)
    merged_df = _merge_snapshot_rows(base_df, snapshot_df)
    items = [_format_stock_item(row) for _, row in merged_df.iterrows()]

    up_count = len([item for item in items if (item.get("change_percent") or 0) > 0])
    down_count = len([item for item in items if (item.get("change_percent") or 0) < 0])
    flat_count = len(items) - up_count - down_count
    total_volume = sum(item.get("volume") or 0 for item in items)
    total_amount = sum(item.get("amount") or 0 for item in items)
    distribution = [
        {"label": "上涨", "value": up_count, "color": "#dc2626"},
        {"label": "下跌", "value": down_count, "color": "#2563eb"},
        {"label": "平盘", "value": flat_count, "color": "#94a3b8"},
    ]
    volume_amount_chart = [
        {
            "code": item["code"],
            "name": item["name"],
            "volume": item.get("volume") or 0,
            "amount": item.get("amount") or 0,
            "change_percent": item.get("change_percent"),
        }
        for item in items
    ]
    return {
        "items": items,
        "summary": {
            "up_count": up_count,
            "down_count": down_count,
            "flat_count": flat_count,
            "total": len(items),
            "total_volume": total_volume,
            "total_amount": total_amount,
        },
        "distribution": distribution,
        "volume_amount_chart": volume_amount_chart,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "live",
        "warning": None,
    }


def fetch_market_change_distribution():
    try:
        snapshot_df = _normalize_stock_directory_df(get_full_market_snapshots())
        source = "eastmoney"
        warning = None
    except Exception as exc:
        try:
            snapshot_df = _normalize_stock_directory_df(get_full_market_snapshots_sina())
            source = "sina"
            warning = f"东方财富源失败，已切换新浪：{exc}"
        except Exception as sina_exc:
            raise RuntimeError(f"全市场涨跌分布获取失败：eastmoney={exc}; sina={sina_exc}") from sina_exc

    bins = list(range(-10, 12, 2))
    labels = [f"{start}%~{start + 2}%" for start in bins[:-1]]
    bucket_counts = {label: 0 for label in labels}
    bucket_counts["< -10%"] = 0
    bucket_counts["> 10%"] = 0
    for value in snapshot_df["change_percent"].dropna().tolist():
        placed = False
        if value < -10:
            bucket_counts["< -10%"] += 1
            continue
        if value > 10:
            bucket_counts["> 10%"] += 1
            continue
        for start, end in zip(bins[:-1], bins[1:]):
            if start <= value < end or (end == 10 and value <= end):
                bucket_counts[f"{start}%~{end}%"] += 1
                placed = True
                break
        if not placed:
            bucket_counts["> 10%"] += 1

    distribution = [{"label": label, "value": count} for label, count in bucket_counts.items()]
    return {
        "distribution": distribution,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "warning": warning,
    }
