import pandas as pd

import akshare as ak

from sentiment.providers.request_utils import call_with_retry


def fetch_global_telegraph():
    return call_with_retry(lambda: ak.stock_info_global_sina(), retries=3, backoff_base=1.2, jitter_seconds=0.5)


def normalize_cls_telegraph(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["title", "summary", "publish_time", "source", "url", "tag"])

    result = df.copy()
    result["publish_time"] = pd.to_datetime(result["时间"], errors="coerce")
    result["source"] = "新浪财经"
    result["url"] = ""
    result["tag"] = "市场快讯"
    result = result.rename(columns={"内容": "summary"})
    result["title"] = result["summary"].astype(str).str.slice(0, 48)
    return result[["title", "summary", "publish_time", "source", "url", "tag"]]
