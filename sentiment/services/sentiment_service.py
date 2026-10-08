import re
import time
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from urllib.parse import quote_plus

import pandas as pd

from core.config import SENTIMENT_CACHE_DIR
from data_sources.akshare_provider import (
    get_industry_constituents,
    get_stock_directory_snapshot,
)
from sentiment.cache_utils import load_cache, save_cache
from sentiment.providers.eastmoney_news_provider import (
    fetch_eastmoney_keyword_news,
    fetch_global_telegraph_em,
    fetch_global_telegraph_ths,
    normalize_em_telegraph,
    normalize_ths_telegraph,
)
from sentiment.providers.sina_feed_provider import (
    fetch_global_telegraph,
    normalize_cls_telegraph,
)
from sentiment.providers.eastmoney_stock_provider import fetch_eastmoney_stock_news
from sentiment.providers.sina_search_provider import (
    fetch_keyword_news,
    fetch_search_api_debug,
    fetch_search_page_debug,
)
from sentiment.providers.sina_stock_provider import fetch_stock_news
from sentiment.schema import SentimentItem


CACHE_DIR = SENTIMENT_CACHE_DIR
CACHE_VERSION = "v10"
MARKET_SENTIMENT_DAYS = 2
SECTOR_SENTIMENT_DAYS = 4
STOCK_SENTIMENT_DAYS = 30
MARKET_SENTIMENT_KEYWORDS = ["A股", "上证指数", "深证成指", "创业板指", "沪深两市"]
MARKET_SENTIMENT_REQUEST_DELAY_SECONDS = 1.2
KEYWORD_PROVIDER_DELAY_SECONDS = 0.8
KEYWORD_LOOP_DELAY_SECONDS = 1.1


def _sleep_safely(seconds):
    if seconds and seconds > 0:
        time.sleep(seconds)


def _normalize_items(df):
    if df is None or df.empty:
        return []

    items = []
    dedupe = set()
    for _, row in df.iterrows():
        publish_time_raw = row.get("publish_time")
        publish_time = pd.to_datetime(publish_time_raw, errors="coerce")
        if pd.isna(publish_time):
            publish_time = _coerce_relative_time(publish_time_raw)
        if pd.isna(publish_time):
            continue

        key = (str(row.get("title", "")).strip(), str(row.get("source", "")).strip(), str(publish_time))
        if key in dedupe:
            continue
        dedupe.add(key)
        items.append(
            SentimentItem(
                title=str(row.get("title", "")).strip() or "未命名资讯",
                summary=str(row.get("summary", "")).strip() or "暂无摘要",
                source=str(row.get("source", "")).strip() or "未知来源",
                publish_time=publish_time.strftime("%Y-%m-%d %H:%M:%S"),
                url=_resolve_item_url(str(row.get("url", "")).strip(), str(row.get("title", "")).strip(), str(row.get("source", "")).strip()),
                tag=str(row.get("tag", "")).strip() or "舆情",
            ).to_dict()
        )
    return items


def _resolve_item_url(raw_url, title, source):
    url = str(raw_url or "").strip()
    if url:
        return url

    keyword = quote_plus(str(title or "").strip())
    source_text = str(source or "").lower()
    if not keyword:
        return ""
    if "东方财富" in source_text or "eastmoney" in source_text:
        return f"https://so.eastmoney.com/news/s?keyword={keyword}"
    if "同花顺" in source_text or "ths" in source_text or "10jqka" in source_text:
        return f"https://search.10jqka.com.cn/?keyword={keyword}"
    if "新浪" in source_text or "sina" in source_text:
        return f"https://search.sina.com.cn/?q={keyword}&c=news&sort=time"
    return f"https://www.baidu.com/s?wd={keyword}"


def _dedupe_similar_titles(items, threshold=0.9):
    if not items:
        return []

    deduped = []
    for item in sorted(items, key=lambda x: str(x.get("publish_time", "")), reverse=True):
        title = str(item.get("title", "") or "").strip()
        if not title:
            deduped.append(item)
            continue

        is_duplicate = False
        for existing in deduped:
            existing_title = str(existing.get("title", "") or "").strip()
            if not existing_title:
                continue
            similarity = SequenceMatcher(None, title, existing_title).ratio()
            if similarity >= threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            deduped.append(item)
    return deduped


def _coerce_relative_time(value):
    text = str(value or "").strip()
    now = datetime.now()
    if not text:
        return pd.NaT
    minute_match = re.match(r"(\d+)\s*分钟前", text)
    if minute_match:
        return now - timedelta(minutes=int(minute_match.group(1)))
    hour_match = re.match(r"(\d+)\s*小时前", text)
    if hour_match:
        return now - timedelta(hours=int(hour_match.group(1)))
    yesterday_match = re.match(r"昨天\s*(\d{2}):(\d{2})", text)
    if yesterday_match:
        return (now - timedelta(days=1)).replace(hour=int(yesterday_match.group(1)), minute=int(yesterday_match.group(2)), second=0, microsecond=0)
    today_match = re.match(r"今天\s*(\d{2}):(\d{2})", text)
    if today_match:
        return now.replace(hour=int(today_match.group(1)), minute=int(today_match.group(2)), second=0, microsecond=0)
    chinese_date_match = re.match(r"(\d{4})年(\d{2})月(\d{2})日\s*(\d{2}):(\d{2})", text)
    if chinese_date_match:
        return datetime(
            year=int(chinese_date_match.group(1)),
            month=int(chinese_date_match.group(2)),
            day=int(chinese_date_match.group(3)),
            hour=int(chinese_date_match.group(4)),
            minute=int(chinese_date_match.group(5)),
            second=0,
            microsecond=0,
        )
    month_day_match = re.match(r"(\d{2})-(\d{2})\s+(\d{2}):(\d{2})", text)
    if month_day_match:
        return now.replace(month=int(month_day_match.group(1)), day=int(month_day_match.group(2)), hour=int(month_day_match.group(3)), minute=int(month_day_match.group(4)), second=0, microsecond=0)
    return pd.to_datetime(text, errors="coerce")


def _filter_items_by_range(items, days=2, start_time=None, end_time=None):
    resolved_end = pd.to_datetime(end_time, errors="coerce") if end_time else pd.Timestamp(datetime.now())
    if pd.isna(resolved_end):
        resolved_end = pd.Timestamp(datetime.now())

    resolved_start = pd.to_datetime(start_time, errors="coerce") if start_time else None
    if resolved_start is None or pd.isna(resolved_start):
        resolved_start = resolved_end - timedelta(days=max(1, days))

    result = []
    for item in items:
        publish_dt = pd.to_datetime(item["publish_time"], errors="coerce")
        if pd.isna(publish_dt):
            continue
        if resolved_start <= publish_dt <= resolved_end:
            result.append(item)
    result.sort(key=lambda x: x["publish_time"], reverse=True)
    return _dedupe_similar_titles(result)


def _cache_file(scope, target, days, start_time=None, end_time=None):
    safe_target = "".join(ch if ch.isalnum() else "_" for ch in str(target or "default")).strip("_") or "default"
    if start_time or end_time:
        start_marker = "".join(ch if ch.isalnum() else "_" for ch in str(start_time or "auto"))
        end_marker = "".join(ch if ch.isalnum() else "_" for ch in str(end_time or "auto"))
        return CACHE_DIR / f"{scope}_{safe_target}_{start_marker}_{end_marker}_{CACHE_VERSION}.json"
    return CACHE_DIR / f"{scope}_{safe_target}_{int(days)}d_{CACHE_VERSION}.json"


def _load_legacy_cache(scope, target, days, max_age_seconds=86400):
    safe_target = "".join(ch if ch.isalnum() else "_" for ch in str(target or "default")).strip("_") or "default"
    pattern = f"{scope}_{safe_target}_{int(days)}d*.json"
    candidates = sorted(CACHE_DIR.glob(pattern), reverse=True)

    current_name = _cache_file(scope, target, days).name
    for path in candidates:
        if path.name == current_name:
            continue
        cached = load_cache(path, max_age_seconds=max_age_seconds)
        if cached and cached.get("items"):
            return cached
    return None


def _build_response(scope, target, items, source, days=2, start_time=None, end_time=None):
    filtered_items = _filter_items_by_range(items, days=days, start_time=start_time, end_time=end_time)
    resolved_end = pd.to_datetime(end_time, errors="coerce") if end_time else pd.Timestamp(datetime.now())
    if pd.isna(resolved_end):
        resolved_end = pd.Timestamp(datetime.now())
    resolved_start = pd.to_datetime(start_time, errors="coerce") if start_time else None
    if resolved_start is None or pd.isna(resolved_start):
        resolved_start = resolved_end - timedelta(days=max(1, days) - 1)
    return {
        "scope": scope,
        "target": target,
        "date_range": [
            resolved_start.strftime("%Y-%m-%d %H:%M:%S"),
            resolved_end.strftime("%Y-%m-%d %H:%M:%S"),
        ],
        "source": source,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": filtered_items,
    }


def _get_stock_name_by_code(stock_code):
    try:
        directory_df = get_stock_directory_snapshot()
    except Exception:
        return ""
    if directory_df is None or directory_df.empty:
        return ""

    matched = directory_df[directory_df["代码"].astype(str).str.strip() == str(stock_code).strip()]
    if matched.empty:
        return ""
    return str(matched.iloc[0]["名称"]).strip()


def _parse_stock_codes(stock_codes):
    normalized = str(stock_codes or "").strip()
    if not normalized:
        return []

    for separator in ["\n", "\t", "，", ",", "、", ";", "；", "|"]:
        normalized = normalized.replace(separator, " ")

    deduped = []
    for item in [part.strip() for part in normalized.split(" ") if part.strip()]:
        if item not in deduped:
            deduped.append(item)
    return deduped


def _get_sector_constituents(sector_name, max_constituents=10):
    records = []
    try:
        sector_response = get_industry_constituents(
            sector_name,
            page=1,
            page_size=max_constituents,
            sort="mktcap",
            asc="0",
        )
        items = sector_response.get("items")
        if isinstance(items, pd.DataFrame) and not items.empty:
            working_items = items.copy()
            if "总市值" in working_items.columns:
                working_items["总市值"] = pd.to_numeric(working_items["总市值"], errors="coerce")
                working_items = working_items.sort_values("总市值", ascending=False, na_position="last")
            for _, row in working_items.head(max_constituents).iterrows():
                code = str(row.get("代码", "") or "").strip()
                name = str(row.get("名称", "") or "").strip()
                if not code and not name:
                    continue
                records.append({"code": code, "name": name})
    except Exception:
        pass
    return records


def _build_sector_stock_terms(sector_name, constituents):
    terms = []
    for item in constituents:
        code = str(item.get("code", "") or "").strip()
        name = str(item.get("name", "") or "").strip()
        candidates = [
            name,
            f"{name} {code}" if name and code else "",
        ]
        for candidate in candidates:
            candidate = str(candidate or "").strip()
            if candidate and candidate not in terms:
                terms.append(candidate)
    if not terms:
        fallback = str(sector_name or "").strip()
        if fallback:
            terms.append(fallback)
    return terms


def _merge_keyword_news(keywords, page_size=12, max_pages=2, debug=False):
    frames = []
    keyword_results = []
    normalized_keywords = [str(keyword or "").strip() for keyword in keywords if str(keyword or "").strip()]
    for index, keyword in enumerate(normalized_keywords):
        keyword = str(keyword or "").strip()
        if not keyword:
            continue
        sina_frame = pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])
        em_frame = pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])
        sina_error = ""
        em_error = ""
        try:
            sina_frame = fetch_keyword_news(keyword, page_size=page_size, max_pages=max_pages)
        except Exception as exc:
            sina_error = str(exc)
        _sleep_safely(KEYWORD_PROVIDER_DELAY_SECONDS)
        try:
            em_frame = fetch_eastmoney_keyword_news(keyword, page_size=page_size, max_pages=max_pages)
        except Exception as exc:
            em_error = str(exc)

        if sina_frame is not None and not sina_frame.empty:
            frames.append(sina_frame)
        if em_frame is not None and not em_frame.empty:
            frames.append(em_frame)

        if debug:
            keyword_results.append(
                {
                    "keyword": keyword,
                    "raw_count": int((0 if sina_frame is None else len(sina_frame)) + (0 if em_frame is None else len(em_frame))),
                    "sina_raw_count": 0 if sina_frame is None else int(len(sina_frame)),
                    "eastmoney_raw_count": 0 if em_frame is None else int(len(em_frame)),
                    "error": " | ".join(item for item in [f"sina: {sina_error}" if sina_error else "", f"eastmoney: {em_error}" if em_error else ""] if item),
                }
            )
        if index < len(normalized_keywords) - 1:
            _sleep_safely(KEYWORD_LOOP_DELAY_SECONDS)

    if not frames:
        merged = pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])
    else:
        merged = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["title", "url"])

    if debug:
        return merged, keyword_results
    return merged


def _build_preview_response(data, limit=10):
    preview = dict(data or {})
    items = list(preview.get("items") or [])
    preview["items"] = items[: max(1, int(limit))]
    preview["is_preview"] = True
    preview["preview_limit"] = max(1, int(limit))
    preview["total_available"] = len(items)
    return preview


def _build_stock_search_terms(stock_code, stock_name):
    code = str(stock_code or "").strip()
    name = str(stock_name or "").strip()
    terms = []
    candidates = [
        code,
        f"{code}.SH" if code.startswith("6") else f"{code}.SZ",
        name,
        f"{name} {code}" if name and code else "",
        f"{name} {code}.SH" if name and code.startswith("6") else "",
        f"{name} {code}.SZ" if name and code and not code.startswith("6") else "",
    ]
    for candidate in candidates:
        candidate = str(candidate or "").strip()
        if candidate and candidate not in terms:
            terms.append(candidate)
    return terms


def _build_code_only_stock_search_terms(stock_code):
    code = str(stock_code or "").strip()
    if not code:
        return []
    terms = [code]
    symbol = f"{code}.SH" if code.startswith("6") else f"{code}.SZ"
    if symbol not in terms:
        terms.append(symbol)
    return terms


def _filter_stock_relevance(df, stock_code, stock_name):
    if df is None or df.empty:
        return pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])

    code = str(stock_code or "").strip()
    name = str(stock_name or "").strip()
    symbol = f"{code}.SH" if code.startswith("6") else f"{code}.SZ"
    code_pattern = re.compile(rf"(?<!\d){re.escape(code)}(?!\d)")
    symbol_pattern = re.compile(rf"(?<![A-Z0-9]){re.escape(symbol)}(?![A-Z0-9])", re.I)

    kept_rows = []
    for _, row in df.iterrows():
        haystack = " ".join(
            [
                str(row.get("title", "") or ""),
                str(row.get("summary", "") or ""),
                str(row.get("url", "") or ""),
            ]
        )
        if code_pattern.search(haystack) or symbol_pattern.search(haystack) or (name and name in haystack):
            kept_rows.append(row.to_dict())

    return pd.DataFrame(kept_rows, columns=["title", "summary", "publish_time", "source", "url", "tag"])


def _filter_sector_relevance(df, sector_name, constituents):
    if df is None or df.empty:
        return pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])

    cleaned_terms = []
    sector_text = str(sector_name or "").strip()
    if sector_text:
        cleaned_terms.append(sector_text)
    for item in constituents:
        code = str(item.get("code", "") or "").strip()
        name = str(item.get("name", "") or "").strip()
        if name and name not in cleaned_terms:
            cleaned_terms.append(name)
        if code and code not in cleaned_terms:
            cleaned_terms.append(code)

    if not cleaned_terms:
        return df

    kept_rows = []
    for _, row in df.iterrows():
        haystack = " ".join(
            [
                str(row.get("title", "") or ""),
                str(row.get("summary", "") or ""),
                str(row.get("url", "") or ""),
            ]
        )
        if any(term in haystack for term in cleaned_terms):
            kept_rows.append(row.to_dict())

    return pd.DataFrame(kept_rows, columns=["title", "summary", "publish_time", "source", "url", "tag"])


def fetch_market_sentiment(days=MARKET_SENTIMENT_DAYS, start_time=None, end_time=None, stage="full"):
    stage = "preview" if str(stage or "").strip().lower() == "preview" else "full"
    custom_range = bool(start_time or end_time)
    cache_file = _cache_file("market", "a_share", days, start_time=start_time, end_time=end_time)
    cached = load_cache(cache_file, max_age_seconds=60) if not custom_range else None
    if cached:
        return cached if stage == "full" else _build_preview_response(cached)

    news_frames = []
    target_keywords = MARKET_SENTIMENT_KEYWORDS[:2] if stage == "preview" else MARKET_SENTIMENT_KEYWORDS
    keyword_page_size = 10 if stage == "preview" else 50
    keyword_max_pages = 1 if stage == "preview" else 2
    for index, keyword in enumerate(target_keywords):
        if index > 0:
            time.sleep(MARKET_SENTIMENT_REQUEST_DELAY_SECONDS)
        try:
            news_frames.append(_merge_keyword_news([keyword], page_size=keyword_page_size, max_pages=keyword_max_pages))
        except Exception:
            continue

    cls_df = normalize_cls_telegraph(fetch_global_telegraph())
    em_fastnews_df = pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])
    ths_fastnews_df = pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])
    try:
        em_fastnews_df = normalize_em_telegraph(fetch_global_telegraph_em())
    except Exception:
        em_fastnews_df = pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])
    try:
        ths_fastnews_df = normalize_ths_telegraph(fetch_global_telegraph_ths())
    except Exception:
        ths_fastnews_df = pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])

    merged = pd.concat(news_frames + [cls_df, em_fastnews_df, ths_fastnews_df], ignore_index=True)
    data = _build_response("market", "A股市场", _normalize_items(merged), source="sina+eastmoney+ths", days=days, start_time=start_time, end_time=end_time)
    if data["items"]:
        if stage == "full":
            save_cache(cache_file, data)
            return data
        return _build_preview_response(data)
    return data if stage == "full" else _build_preview_response(data)


def fetch_sector_sentiment(sector_name, days=SECTOR_SENTIMENT_DAYS, start_time=None, end_time=None, stage="full"):
    if not sector_name:
        raise ValueError("请输入板块名称")
    stage = "preview" if str(stage or "").strip().lower() == "preview" else "full"

    custom_range = bool(start_time or end_time)
    cache_file = _cache_file("sector", sector_name, days, start_time=start_time, end_time=end_time)
    cached = load_cache(cache_file, max_age_seconds=600) if not custom_range else None
    if cached:
        return cached if stage == "full" else _build_preview_response(cached)

    legacy_cached = _load_legacy_cache("sector", sector_name, days) if not custom_range else None
    if legacy_cached:
        save_cache(cache_file, legacy_cached)
        return legacy_cached if stage == "full" else _build_preview_response(legacy_cached)

    constituents = _get_sector_constituents(sector_name, max_constituents=6 if stage == "preview" else 10)
    search_terms = _build_sector_stock_terms(sector_name, constituents)
    if stage == "preview":
        search_terms = search_terms[:3] or [sector_name]
    sector_df = _merge_keyword_news(search_terms, page_size=6 if stage == "preview" else 10, max_pages=1 if stage == "preview" else 2)
    relevant_sector_df = _filter_sector_relevance(sector_df, sector_name, constituents)
    data = _build_response("sector", sector_name, _normalize_items(relevant_sector_df), source="sina+eastmoney", days=days, start_time=start_time, end_time=end_time)
    if data["items"]:
        if stage == "full":
            save_cache(cache_file, data)
            return data
        return _build_preview_response(data)

    legacy_cached = _load_legacy_cache("sector", sector_name, days, max_age_seconds=7 * 86400) if not custom_range else None
    if legacy_cached:
        save_cache(cache_file, legacy_cached)
        return legacy_cached if stage == "full" else _build_preview_response(legacy_cached)
    return data if stage == "full" else _build_preview_response(data)


def fetch_stock_sentiment(stock_code, days=STOCK_SENTIMENT_DAYS, debug=False, start_time=None, end_time=None, stage="full"):
    if not stock_code:
        raise ValueError("请输入股票代码")
    stage = "preview" if str(stage or "").strip().lower() == "preview" else "full"

    custom_range = bool(start_time or end_time)
    cache_file = _cache_file("stock", stock_code, days, start_time=start_time, end_time=end_time)
    cached = load_cache(cache_file, max_age_seconds=300) if not debug and not custom_range else None
    if cached and not debug:
        return cached if stage == "full" else _build_preview_response(cached)

    if not debug and not custom_range:
        legacy_cached = _load_legacy_cache("stock", stock_code, days)
        if legacy_cached:
            return legacy_cached if stage == "full" else _build_preview_response(legacy_cached)

    stock_name = ""
    code_keywords = _build_code_only_stock_search_terms(stock_code)
    keywords = code_keywords[:]

    stock_page_df = pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])
    stock_page_error = ""
    try:
        stock_page_df = fetch_stock_news(stock_code, max_pages=1 if stage == "preview" else 3)
    except Exception as exc:
        stock_page_error = str(exc)

    eastmoney_df = pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])
    eastmoney_error = ""
    try:
        eastmoney_df = fetch_eastmoney_stock_news(stock_code, limit=10 if stage == "preview" else 20)
    except Exception as exc:
        eastmoney_error = str(exc)

    merge_result = _merge_keyword_news(
        code_keywords[:1] if stage == "preview" else code_keywords,
        page_size=8 if stage == "preview" else 12,
        max_pages=1 if stage == "preview" else 2,
        debug=debug,
    )
    if debug:
        search_df, keyword_results = merge_result
    else:
        search_df = merge_result
        keyword_results = []

    stock_df = pd.concat([stock_page_df, eastmoney_df, search_df], ignore_index=True)
    relevant_stock_df = _filter_stock_relevance(stock_df, stock_code, stock_name)
    focused_fallback_used = False
    focused_fallback_count = 0

    if relevant_stock_df is None or relevant_stock_df.empty:
        stock_name = _get_stock_name_by_code(stock_code)
        keywords = _build_stock_search_terms(stock_code, stock_name)
        extra_keywords = [keyword for keyword in keywords if keyword not in code_keywords]
        if extra_keywords:
            merge_result = _merge_keyword_news(extra_keywords, page_size=12, max_pages=2, debug=debug)
            if debug:
                extra_search_df, extra_keyword_results = merge_result
                keyword_results.extend(extra_keyword_results)
            else:
                extra_search_df = merge_result
            stock_df = pd.concat([stock_df, extra_search_df], ignore_index=True)
            relevant_stock_df = _filter_stock_relevance(stock_df, stock_code, stock_name)

    if relevant_stock_df is None or relevant_stock_df.empty:
        focused_fallback_used = True
        fallback_frames = []
        fallback_terms = [str(stock_code or "").strip()]
        symbol = f"{stock_code}.SH" if str(stock_code).startswith("6") else f"{stock_code}.SZ"
        if symbol not in fallback_terms:
            fallback_terms.append(symbol)

        for fallback_term in fallback_terms:
            try:
                fallback_frame = fetch_keyword_news(fallback_term, page_size=10, max_pages=1)
            except Exception:
                continue
            if fallback_frame is not None and not fallback_frame.empty:
                fallback_frames.append(fallback_frame)

        if fallback_frames:
            focused_search_df = pd.concat(fallback_frames, ignore_index=True)
            focused_fallback_count = int(len(focused_search_df))
            stock_df = pd.concat([stock_df, focused_search_df], ignore_index=True)
            relevant_stock_df = _filter_stock_relevance(stock_df, stock_code, stock_name)

    normalized_items = _normalize_items(relevant_stock_df)
    data = _build_response("stock", stock_code, normalized_items, source="sina+eastmoney", days=days, start_time=start_time, end_time=end_time)
    if debug:
        search_page_debug = []
        for keyword in keywords[:5]:
            try:
                search_page_debug.append(fetch_search_page_debug(keyword, page_size=10))
            except Exception as exc:
                search_page_debug.append(
                    {
                        "keyword": keyword,
                        "html_title": "",
                        "html_length": 0,
                        "parsed_count": 0,
                        "html_preview": "",
                        "error": str(exc),
                    }
                )
        search_api_debug = []
        for keyword in keywords[:5]:
            try:
                search_api_debug.append(fetch_search_api_debug(keyword, page_size=10))
            except Exception as exc:
                search_api_debug.append(
                    {
                        "keyword": keyword,
                        "request_url": "",
                        "status_code": 0,
                        "content_type": "",
                        "server": "",
                        "set_cookie": False,
                        "json_ok": False,
                        "json_code": None,
                        "list_count": 0,
                        "body_preview": "",
                        "error": str(exc),
                    }
                )
        data["debug"] = {
            "target": stock_code,
            "stock_name": stock_name,
            "keywords": keywords,
            "raw_item_count": 0 if stock_df is None else int(len(stock_df)),
            "relevant_raw_count": 0 if relevant_stock_df is None else int(len(relevant_stock_df)),
            "stock_page_raw_count": 0 if stock_page_df is None else int(len(stock_page_df)),
            "eastmoney_raw_count": 0 if eastmoney_df is None else int(len(eastmoney_df)),
            "search_raw_count": 0 if search_df is None else int(len(search_df)),
            "stock_page_error": stock_page_error,
            "eastmoney_error": eastmoney_error,
            "focused_fallback_used": focused_fallback_used,
            "focused_fallback_count": focused_fallback_count,
            "normalized_count": len(normalized_items),
            "filtered_count": len(data["items"]),
            "keyword_results": keyword_results,
            "search_page_debug": search_page_debug,
            "search_api_debug": search_api_debug,
        }
    if data["items"] and not debug and stage == "full":
        save_cache(cache_file, data)
    return data if stage == "full" else _build_preview_response(data)


def fetch_multi_stock_sentiment(stock_codes, days=STOCK_SENTIMENT_DAYS, start_time=None, end_time=None, stage="full"):
    parsed_codes = _parse_stock_codes(stock_codes)
    if not parsed_codes:
        raise ValueError("请输入至少一个股票代码")

    all_items = []
    targets = []
    for stock_code in parsed_codes:
        stock_data = fetch_stock_sentiment(stock_code, days=days, debug=False, start_time=start_time, end_time=end_time, stage=stage)
        all_items.extend(stock_data.get("items", []))
        targets.append(stock_code)

    resolved_end = pd.to_datetime(end_time, errors="coerce") if end_time else pd.Timestamp(datetime.now())
    if pd.isna(resolved_end):
        resolved_end = pd.Timestamp(datetime.now())
    resolved_start = pd.to_datetime(start_time, errors="coerce") if start_time else resolved_end - timedelta(days=max(1, days) - 1)
    if pd.isna(resolved_start):
        resolved_start = resolved_end - timedelta(days=max(1, days) - 1)

    response = {
        "scope": "stock",
        "target": "、".join(targets),
        "date_range": [
            resolved_start.strftime("%Y-%m-%d %H:%M:%S"),
            resolved_end.strftime("%Y-%m-%d %H:%M:%S"),
        ],
        "source": "sina+eastmoney",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": _filter_items_by_range(all_items, days=days, start_time=start_time, end_time=end_time),
    }
    return response if str(stage or "").strip().lower() != "preview" else _build_preview_response(response)
