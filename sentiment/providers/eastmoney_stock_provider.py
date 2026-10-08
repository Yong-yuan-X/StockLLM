import pandas as pd

import akshare as ak

from sentiment.providers.request_utils import call_with_retry, sleep_with_jitter


def fetch_eastmoney_stock_news(stock_code, limit=20):
    """Fetch stock news from Eastmoney via AkShare."""
    code = str(stock_code or "").strip()
    if not code:
        raise ValueError("请输入股票代码")

    sleep_with_jitter(0.6, 0.35)
    df = call_with_retry(lambda: ak.stock_news_em(symbol=code), retries=3, backoff_base=1.2, jitter_seconds=0.5)
    if df is None or df.empty:
        return pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])

    working_df = df.copy()
    rename_map = {
        "新闻标题": "title",
        "新闻内容": "summary",
        "发布时间": "publish_time",
        "文章来源": "source",
        "新闻链接": "url",
        "关键词": "tag",
    }
    working_df = working_df.rename(columns=rename_map)

    for column in ["title", "summary", "publish_time", "source", "url", "tag"]:
        if column not in working_df.columns:
            working_df[column] = ""

    working_df["title"] = working_df["title"].astype(str).str.strip()
    working_df["summary"] = working_df["summary"].astype(str).str.strip()
    working_df["publish_time"] = working_df["publish_time"].astype(str).str.strip()
    working_df["source"] = working_df["source"].astype(str).str.strip().replace("", "东方财富")
    working_df["url"] = working_df["url"].astype(str).str.strip()
    working_df["tag"] = code

    working_df = working_df[
        (working_df["title"] != "")
        & (working_df["publish_time"] != "")
        & (working_df["url"] != "")
    ].drop_duplicates(subset=["title", "url"])

    if limit:
        working_df = working_df.head(max(1, int(limit)))

    return working_df[["title", "summary", "publish_time", "source", "url", "tag"]].reset_index(drop=True)
