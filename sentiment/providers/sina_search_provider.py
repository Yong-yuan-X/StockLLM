import re
from html import unescape

import pandas as pd
import requests

from sentiment.providers.request_utils import request_get_with_retry, sleep_with_jitter


SEARCH_URL = "https://search.sina.com.cn/"
SEARCH_API_URL = "https://search.sina.com.cn/api/news"
SEARCH_HEADERS = {
    "referer": "https://search.sina.com.cn/",
    "user-agent": "Mozilla/5.0",
}
SEARCH_REQUEST_GAP_SECONDS = 0.5
TIME_PATTERN = (
    r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|"
    r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}|"
    r"\d{4}年\d{2}月\d{2}日\s*\d{2}:\d{2}|"
    r"\d{2}-\d{2}\s+\d{2}:\d{2}|"
    r"\d+\s*(?:分钟前|小时前)|"
    r"今天\s*\d{2}:\d{2}|"
    r"昨天\s*\d{2}:\d{2}"
)


def _clean_html_text(value):
    text = re.sub(r"<[^>]+>", "", str(value or ""))
    return unescape(text).replace("\u3000", " ").replace("&nbsp;", " ").strip()


def _extract_records_from_html(html, keyword):
    blocks = re.findall(r'(<div[^>]+class="box-result clearfix"[^>]*>.*?</div>\s*</div>)', html, flags=re.S)
    if not blocks:
        blocks = re.findall(r'(<div[^>]*class="box-result[^"]*"[^>]*>.*?</div>\s*</div>)', html, flags=re.S)
    if not blocks:
        blocks = re.findall(r'(<h2>.*?(?:<p class="content">.*?</p>)?.*?<span class="fgray_time">.*?</span>.*?(?:</div>|</h2>))', html, flags=re.S)
    if not blocks:
        blocks = re.findall(r'(<div[^>]*>.*?(?:新浪|news|result).*?</div>)', html, flags=re.S)

    records = []
    for block in blocks:
        link_match = re.search(r"<h2[^>]*>.*?<a[^>]+href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", block, flags=re.S)
        if not link_match:
            link_match = re.search(r"<a[^>]+href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", block, flags=re.S)
        if not link_match:
            continue

        url = link_match.group(1).strip()
        title = _clean_html_text(link_match.group(2))
        summary_match = re.search(r'<p[^>]+class="content"[^>]*>(.*?)</p>', block, flags=re.S)
        summary = _clean_html_text(summary_match.group(1)) if summary_match else ""
        time_match = re.search(r"<span[^>]+class=['\"][^'\"]*(?:fgray_time|news-time|feed-time|time|date)[^'\"]*['\"][^>]*>(.*?)</span>", block, flags=re.S)
        if not time_match:
            time_match = re.search(rf"({TIME_PATTERN})", block, flags=re.S)
        source = "新浪财经"
        publish_time_text = ""
        if time_match:
            meta_text = _clean_html_text(time_match.group(1))
            time_parts = re.findall(
                TIME_PATTERN,
                meta_text,
            )
            publish_time_text = time_parts[-1] if time_parts else meta_text
            source_text = meta_text.replace(publish_time_text, "").strip(" _-|")
            if source_text:
                source = source_text

        records.append(
            {
                "title": title or "未命名资讯",
                "summary": summary or "暂无摘要",
                "publish_time": publish_time_text,
                "source": source,
                "url": url,
                "tag": str(keyword).strip(),
            }
        )

    if records:
        return records

    # 兜底：搜索页样式变动时，不再依赖特定 block class，直接按“标题链接 + 时间”扫描全文。
    fallback_patterns = [
        re.compile(
            rf"<a[^>]+href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>.{{0,3000}}?({TIME_PATTERN})",
            flags=re.S,
        ),
        re.compile(
            rf"({TIME_PATTERN}).{{0,3000}}?<a[^>]+href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>",
            flags=re.S,
        ),
    ]

    seen = set()
    for pattern in fallback_patterns:
        for match in pattern.findall(html):
            if len(match) != 3:
                continue

            if pattern.pattern.startswith('<a'):
                url, title, publish_time_text = match
            else:
                publish_time_text, url, title = match

            url = str(url or "").strip()
            title = _clean_html_text(title)
            publish_time_text = str(publish_time_text or "").strip()

            if not title or not url or not publish_time_text:
                continue
            if not url.startswith("http"):
                continue

            dedupe_key = (title, url)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            records.append(
                {
                    "title": title,
                    "summary": "来自新浪搜索结果页",
                    "publish_time": publish_time_text,
                    "source": "新浪搜索",
                    "url": url,
                    "tag": str(keyword).strip(),
                }
            )
    return records


def _fetch_search_page_response(keyword, page, page_size):
    sleep_with_jitter(SEARCH_REQUEST_GAP_SECONDS, 0.3)
    response = request_get_with_retry(
        SEARCH_URL,
        params={
            "q": str(keyword).strip(),
            "tp": "mix",
            "sort": 1,
            "page": page,
            "size": page_size,
            "from": "search_result",
        },
        headers=SEARCH_HEADERS,
        timeout=15,
        retries=3,
        backoff_base=1.0,
        jitter_seconds=0.5,
    )
    response.encoding = response.apparent_encoding or "utf-8"
    return response


def _fetch_search_page_html(keyword, page, page_size):
    return _fetch_search_page_response(keyword, page, page_size).text


def fetch_search_page_debug(keyword, page_size=10):
    response = _fetch_search_page_response(keyword, page=1, page_size=page_size)
    html = response.text
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.S | re.I)
    parsed = _extract_records_from_html(html, keyword)
    return {
        "keyword": str(keyword).strip(),
        "request_url": response.url,
        "status_code": response.status_code,
        "content_type": response.headers.get("Content-Type", ""),
        "server": response.headers.get("Server", ""),
        "set_cookie": bool(response.headers.get("Set-Cookie")),
        "html_title": _clean_html_text(title_match.group(1)) if title_match else "",
        "html_length": len(html),
        "parsed_count": len(parsed),
        "html_preview": _clean_html_text(html[:1200]),
        "html_preview_raw": html[:1200],
    }


def fetch_search_api_debug(keyword, page_size=10):
    sleep_with_jitter(SEARCH_REQUEST_GAP_SECONDS, 0.3)
    response = request_get_with_retry(
        SEARCH_API_URL,
        params={
            "q": str(keyword).strip(),
            "page": 1,
            "size": page_size,
            "sort": 1,
            "tp": "mix",
            "from": "search_result",
        },
        headers=SEARCH_HEADERS,
        timeout=15,
        retries=3,
        backoff_base=1.0,
        jitter_seconds=0.5,
    )
    response.encoding = response.apparent_encoding or "utf-8"
    body_text = response.text
    try:
        payload = response.json()
        data = payload.get("data") or {}
        list_count = len(data.get("list") or [])
    except Exception:
        payload = None
        list_count = 0

    return {
        "keyword": str(keyword).strip(),
        "request_url": response.url,
        "status_code": response.status_code,
        "content_type": response.headers.get("Content-Type", ""),
        "server": response.headers.get("Server", ""),
        "set_cookie": bool(response.headers.get("Set-Cookie")),
        "json_ok": payload is not None,
        "json_code": None if payload is None else payload.get("code"),
        "list_count": list_count,
        "body_preview": body_text[:800],
    }


def fetch_keyword_news(keyword, page_size=20, max_pages=3):
    page_size = max(10, min(int(page_size), 50))
    max_pages = max(1, min(int(max_pages), 5))
    records = []
    seen = set()

    for page in range(1, max_pages + 1):
        page_records = []
        try:
            sleep_with_jitter(SEARCH_REQUEST_GAP_SECONDS, 0.3)
            response = request_get_with_retry(
                SEARCH_API_URL,
                params={
                    "q": str(keyword).strip(),
                    "page": page,
                    "size": page_size,
                    "sort": 1,
                    "tp": "mix",
                    "from": "search_result",
                },
                headers=SEARCH_HEADERS,
                timeout=15,
                retries=3,
                backoff_base=1.0,
                jitter_seconds=0.5,
            )
            response.encoding = response.apparent_encoding or "utf-8"
            payload = response.json()
            if response.status_code == 429 or payload.get("code") not in (0, "0", None):
                page_records = _extract_records_from_html(_fetch_search_page_html(keyword, page, page_size), keyword)
                payload = None
            if payload is None:
                pass
            else:
                data = payload.get("data") or {}
                items = data.get("list") or []
                for item in items:
                    title = _clean_html_text(item.get("title"))
                    summary = _clean_html_text(item.get("searchSummary") or item.get("intro"))
                    publish_time = str(item.get("time") or item.get("dataTime") or "").strip()
                    source = (
                        _clean_html_text(item.get("media_show"))
                        or _clean_html_text(((item.get("source") or {}).get("media")))
                        or "新浪财经"
                    )
                    url = str(item.get("url") or "").strip()
                    if not title or not url:
                        continue
                    page_records.append(
                        {
                            "title": title,
                            "summary": summary or "暂无摘要",
                            "publish_time": publish_time,
                            "source": source,
                            "url": url,
                            "tag": str(keyword).strip(),
                        }
                    )

                # 新浪搜索接口有时会正常返回，但 list 为空；这时继续回退到 HTML 搜索结果页，
                # 以免遗漏像纯股票代码这类在页面上能搜到、接口却不给结果的场景。
                if not page_records:
                    page_records = _extract_records_from_html(_fetch_search_page_html(keyword, page, page_size), keyword)
        except ValueError:
            page_records = _extract_records_from_html(response.text, keyword)
        except requests.RequestException:
            try:
                page_records = _extract_records_from_html(_fetch_search_page_html(keyword, page, page_size), keyword)
            except requests.RequestException:
                page_records = []

        if not page_records:
            continue

        for record in page_records:
            dedupe_key = (record["title"], record["url"])
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            records.append(record)

        if len(page_records) < max(5, page_size // 2):
            break

    return pd.DataFrame(records, columns=["title", "summary", "publish_time", "source", "url", "tag"])
