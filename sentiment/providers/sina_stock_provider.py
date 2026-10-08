import re
from html import unescape

import pandas as pd
import requests

from sentiment.providers.request_utils import request_get_with_retry, sleep_with_jitter


STOCK_HEADERS = {
    "referer": "https://finance.sina.com.cn/",
    "user-agent": "Mozilla/5.0",
}


def _clean_html_text(value):
    text = re.sub(r"<[^>]+>", "", str(value or ""))
    return unescape(text).replace("\u3000", " ").replace("&nbsp;", " ").strip()


def _to_sina_symbol(stock_code):
    code = str(stock_code or "").strip()
    if not code:
        raise ValueError("请输入股票代码")
    return f"sh{code}" if code.startswith("6") else f"sz{code}"


def _extract_stock_news_records(html, stock_code):
    records = []
    seen = set()

    patterns = [
        re.compile(
            r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}).{0,1200}?<a[^>]+href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>",
            flags=re.S,
        ),
        re.compile(
            r"<a[^>]+href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>.{0,1200}?(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})",
            flags=re.S,
        ),
    ]

    for pattern in patterns:
        for match in pattern.finditer(html):
            if len(match.groups()) != 3:
                continue

            if pattern.pattern.startswith("(\\d{4}"):
                publish_time, url, title = match.groups()
            else:
                url, title, publish_time = match.groups()

            url = str(url or "").strip()
            title = _clean_html_text(title)
            publish_time = str(publish_time or "").strip()

            if not url or not title or not publish_time:
                continue
            if not url.startswith("http"):
                continue
            if "新浪财经" in title and "个股资讯" in title:
                continue

            dedupe_key = (title, url)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            records.append(
                {
                    "title": title,
                    "summary": "来自新浪个股资讯页",
                    "publish_time": publish_time,
                    "source": "新浪财经",
                    "url": url,
                    "tag": str(stock_code).strip(),
                }
            )

    if records:
        return records

    # 兜底：当前新浪个股资讯页结构有时更扁平，时间与链接不一定紧邻。
    # 这里直接在全文里寻找“时间 + 标题链接”组合，尽量保住可见新闻。
    fallback_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}).{0,3000}?<a[^>]+href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>",
        flags=re.S,
    )
    for publish_time, url, title in fallback_pattern.findall(html):
        url = str(url or "").strip()
        title = _clean_html_text(title)
        publish_time = str(publish_time or "").strip()

        if not url or not title or not publish_time:
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
                "summary": "来自新浪个股资讯页",
                "publish_time": publish_time,
                "source": "新浪财经",
                "url": url,
                "tag": str(stock_code).strip(),
            }
        )

    return records


def fetch_stock_news(stock_code, max_pages=3):
    symbol = _to_sina_symbol(stock_code)
    max_pages = max(1, min(int(max_pages), 5))
    records = []
    seen = set()

    for page in range(1, max_pages + 1):
        sleep_with_jitter(0.6, 0.35)
        if page == 1:
            response = request_get_with_retry(
                f"https://money.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/{symbol}.phtml",
                headers=STOCK_HEADERS,
                timeout=15,
                retries=3,
                backoff_base=1.0,
                jitter_seconds=0.5,
            )
        else:
            response = request_get_with_retry(
                "https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllNewsStock.php",
                params={"Page": page, "symbol": symbol},
                headers=STOCK_HEADERS,
                timeout=15,
                retries=3,
                backoff_base=1.0,
                jitter_seconds=0.5,
            )

        response.encoding = response.apparent_encoding or "gbk"
        page_records = _extract_stock_news_records(response.text, stock_code)
        if not page_records:
            continue

        for record in page_records:
            dedupe_key = (record["title"], record["url"])
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            records.append(record)

    return pd.DataFrame(records, columns=["title", "summary", "publish_time", "source", "url", "tag"])
