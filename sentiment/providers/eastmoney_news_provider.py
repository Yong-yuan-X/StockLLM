import json
import time

import akshare as ak
import pandas as pd
import requests

from sentiment.providers.request_utils import call_with_retry, request_get_with_retry, sleep_with_jitter


EASTMONEY_SEARCH_URL = "https://search-api-web.eastmoney.com/search/jsonp"
EASTMONEY_SEARCH_HEADERS = {
    "accept": "*/*",
    "referer": "https://so.eastmoney.com/news/s",
    "user-agent": "Mozilla/5.0",
}
EASTMONEY_PAGE_DELAY_SECONDS = 0.9


def fetch_eastmoney_keyword_news(keyword, page_size=10, max_pages=3):
    text = str(keyword or "").strip()
    if not text:
        return pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])

    page_size = max(10, min(int(page_size), 50))
    max_pages = max(1, min(int(max_pages), 5))
    frames = []

    for page in range(1, max_pages + 1):
        inner_param = {
            "uid": "",
            "keyword": text,
            "type": ["cmsArticleWebOld"],
            "client": "web",
            "clientType": "web",
            "clientVersion": "curr",
            "param": {
                "cmsArticleWebOld": {
                    "searchScope": "default",
                    "sort": "default",
                    "pageIndex": page,
                    "pageSize": page_size,
                    "preTag": "<em>",
                    "postTag": "</em>",
                }
            },
        }
        params = {
            "cb": f"jQuery_keyword_{page}",
            "param": json.dumps(inner_param, ensure_ascii=False),
            "_": str(1700000000000 + page),
        }

        sleep_with_jitter(0.5, 0.35)
        response = request_get_with_retry(
            EASTMONEY_SEARCH_URL,
            params=params,
            headers=EASTMONEY_SEARCH_HEADERS,
            timeout=15,
            retries=3,
            backoff_base=1.0,
            jitter_seconds=0.5,
        )
        response.encoding = response.apparent_encoding or "utf-8"
        payload_text = response.text.strip()
        if "(" not in payload_text or not payload_text.endswith(")"):
            continue

        payload = json.loads(payload_text[payload_text.find("(") + 1 : -1])
        items = (((payload.get("result") or {}).get("cmsArticleWebOld")) or [])
        if not items:
            continue

        frame = pd.DataFrame(items)
        if frame.empty:
            continue

        frame["url"] = "http://finance.eastmoney.com/a/" + frame["code"].astype(str) + ".html"
        frame = frame.rename(
            columns={
                "title": "title",
                "content": "summary",
                "date": "publish_time",
                "mediaName": "source",
                "url": "url",
            }
        )

        for column in ["title", "summary", "publish_time", "source", "url"]:
            if column not in frame.columns:
                frame[column] = ""

        frame["title"] = (
            frame["title"].astype(str).str.replace(r"</?em>", "", regex=True).str.strip()
        )
        frame["summary"] = (
            frame["summary"]
            .astype(str)
            .str.replace(r"</?em>", "", regex=True)
            .str.replace(r"\u3000", " ", regex=True)
            .str.replace(r"\r\n", " ", regex=True)
            .str.strip()
        )
        frame["publish_time"] = frame["publish_time"].astype(str).str.strip()
        frame["source"] = frame["source"].astype(str).str.strip().replace("", "东方财富")
        frame["url"] = frame["url"].astype(str).str.strip()
        frame["tag"] = text

        frame = frame[
            (frame["title"] != "") & (frame["publish_time"] != "") & (frame["url"] != "")
        ][["title", "summary", "publish_time", "source", "url", "tag"]]

        if not frame.empty:
            frames.append(frame)

        if len(items) < page_size:
            break
        time.sleep(EASTMONEY_PAGE_DELAY_SECONDS)

    if not frames:
        return pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])

    return pd.concat(frames, ignore_index=True).drop_duplicates(subset=["title", "url"]).reset_index(drop=True)


def fetch_global_telegraph_em():
    return call_with_retry(lambda: ak.stock_info_global_em(), retries=3, backoff_base=1.2, jitter_seconds=0.5)


def fetch_global_telegraph_ths():
    return call_with_retry(lambda: ak.stock_info_global_ths(), retries=3, backoff_base=1.2, jitter_seconds=0.5)


def normalize_em_telegraph(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])

    result = df.copy()
    rename_map = {
        "标题": "title",
        "摘要": "summary",
        "发布时间": "publish_time",
        "链接": "url",
    }
    result = result.rename(columns=rename_map)
    for column in ["title", "summary", "publish_time", "url"]:
        if column not in result.columns:
            result[column] = ""

    result["source"] = "东方财富"
    result["tag"] = "市场快讯"
    result["title"] = result["title"].astype(str).str.strip()
    result["summary"] = result["summary"].astype(str).str.strip()
    result["publish_time"] = result["publish_time"].astype(str).str.strip()
    result["url"] = result["url"].astype(str).str.strip()
    return result[["title", "summary", "publish_time", "source", "url", "tag"]]


def normalize_ths_telegraph(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])

    result = df.copy()
    rename_map = {
        "标题": "title",
        "内容": "summary",
        "发布时间": "publish_time",
        "时间": "publish_time",
        "链接": "url",
    }
    result = result.rename(columns=rename_map)
    for column in ["title", "summary", "publish_time", "url"]:
        if column not in result.columns:
            result[column] = ""

    result["source"] = "同花顺"
    result["tag"] = "市场快讯"
    result["title"] = result["title"].astype(str).str.strip()
    result["summary"] = result["summary"].astype(str).str.strip()
    result["publish_time"] = result["publish_time"].astype(str).str.strip()
    result["url"] = result["url"].astype(str).str.strip()
    return result[["title", "summary", "publish_time", "source", "url", "tag"]]
