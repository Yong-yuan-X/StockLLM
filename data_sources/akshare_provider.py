from datetime import datetime
import json
import time

import akshare as ak
import pandas as pd
import requests


INDEX_CONFIG = {
    "sh000001": {"symbol": "sh000001", "fallback_symbol": "000001"},
    "sz399001": {"symbol": "sz399001", "fallback_symbol": "399001"},
    "sz399006": {"symbol": "sz399006", "fallback_symbol": "399006"},
}

SINA_SECTOR_OVERRIDES = {
    "小金属": "sw2_240500",
    "证券": "sw2_490100",
    "银行": "sw1_480000",
    "半导体": "sw2_270100",
    "人工智能": "chgn_700230",
}

SINA_HEADERS = {
    "Referer": "https://finance.sina.com.cn",
    "User-Agent": "Mozilla/5.0",
}


def get_stock_history(stock_code, start_date, end_date, adjust="qfq"):
    normalized_code = str(stock_code).strip()
    primary_error = None

    for attempt in range(3):
        try:
            return _fetch_stock_history_eastmoney(normalized_code, start_date, end_date, adjust)
        except Exception as exc:
            primary_error = exc
            if attempt < 2:
                time.sleep(3)

    try:
        return _fetch_stock_history_tencent(normalized_code, start_date, end_date, adjust)
    except Exception as fallback_exc:
        raise RuntimeError(
            f"东方财富历史数据拉取失败（已重试 2 次）后，腾讯历史数据也失败。"
            f" primary_error={primary_error}; fallback_error={fallback_exc}"
        ) from fallback_exc


def _fetch_stock_history_eastmoney(stock_code, start_date, end_date, adjust="qfq"):
    df = ak.stock_zh_a_hist(
        symbol=stock_code,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )
    normalized = _normalize_stock_history_df(df, source="eastmoney", stock_code=stock_code)
    normalized.attrs["source"] = "eastmoney"
    return normalized


def _fetch_stock_history_tencent(stock_code, start_date, end_date, adjust="qfq"):
    tx_symbol = _to_tx_stock_symbol(stock_code)
    df = ak.stock_zh_a_hist_tx(
        symbol=tx_symbol,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )
    normalized = _normalize_stock_history_df(df, source="tencent", stock_code=stock_code)
    start_dt = pd.to_datetime(start_date, format="%Y%m%d")
    end_dt = pd.to_datetime(end_date, format="%Y%m%d")
    normalized = normalized[
        (normalized["trade_date"] >= start_dt) & (normalized["trade_date"] <= end_dt)
    ].reset_index(drop=True)
    normalized.attrs["source"] = "tencent"
    return normalized


def get_stock_intraday(stock_code):
    normalized_code = str(stock_code).strip()
    df = ak.stock_zh_a_hist_min_em(
        symbol=normalized_code,
        period="5",
        adjust="",
    )
    if df is None or df.empty:
        raise ValueError(f"未获取到 {stock_code} 的分时数据")

    working_df = df.copy()
    rename_map = {
        "时间": "trade_date",
        "日期时间": "trade_date",
        "datetime": "trade_date",
        "开盘": "open",
        "最高": "high",
        "最低": "low",
        "收盘": "close",
        "成交量": "volume",
        "成交额": "amount",
        "涨跌幅": "pct_chg",
        "涨跌额": "change",
    }
    working_df = working_df.rename(columns={col: rename_map[col] for col in working_df.columns if col in rename_map}).copy()
    if "trade_date" not in working_df.columns or "close" not in working_df.columns:
        raise ValueError(f"{stock_code} 分时数据字段异常")

    working_df["trade_date"] = pd.to_datetime(working_df["trade_date"], errors="coerce")
    for col in ["open", "high", "low", "close", "volume", "amount", "pct_chg", "change"]:
        if col in working_df.columns:
            working_df[col] = pd.to_numeric(working_df[col], errors="coerce")
        else:
            working_df[col] = None

    today = pd.Timestamp(datetime.now().date())
    working_df = working_df[working_df["trade_date"].dt.normalize() == today].dropna(subset=["trade_date", "close"])
    if working_df.empty:
        raise ValueError(f"{stock_code} 当天暂无分时数据")

    if "change" not in working_df.columns or working_df["change"].isna().all():
        working_df["change"] = working_df["close"].diff()
    if "pct_chg" not in working_df.columns or working_df["pct_chg"].isna().all():
        working_df["pct_chg"] = working_df["close"].pct_change() * 100
    working_df["preclose"] = working_df["close"].shift(1)
    working_df["turn"] = None
    working_df = working_df.sort_values("trade_date").reset_index(drop=True)
    working_df.attrs["source"] = "eastmoney_intraday"
    return working_df


def _normalize_stock_history_df(df, source, stock_code):
    if df is None or df.empty:
        raise ValueError(f"未获取到 {stock_code} 的历史数据，source={source}")

    normalized = df.copy()
    if source == "eastmoney":
        normalized["trade_date"] = pd.to_datetime(normalized["日期"])
        rename_map = {
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "涨跌额": "change",
            "涨跌幅": "pct_chg",
            "成交量": "volume",
            "成交额": "amount",
        }
        normalized = normalized.rename(columns=rename_map)
        numeric_columns = ["open", "high", "low", "close", "change", "pct_chg", "volume", "amount"]
        for col in numeric_columns:
            if col in normalized.columns:
                normalized[col] = pd.to_numeric(normalized[col], errors="coerce")
        normalized["preclose"] = normalized["close"] - normalized["change"]
        normalized["turn"] = pd.to_numeric(normalized["换手率"], errors="coerce") if "换手率" in normalized.columns else None
    elif source == "tencent":
        normalized["trade_date"] = pd.to_datetime(normalized["date"])
        rename_map = {
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "amount": "amount",
        }
        normalized = normalized.rename(columns=rename_map)
        numeric_columns = ["open", "high", "low", "close", "amount"]
        for col in numeric_columns:
            if col in normalized.columns:
                normalized[col] = pd.to_numeric(normalized[col], errors="coerce")
        normalized = normalized.sort_values("trade_date").reset_index(drop=True)
        normalized["change"] = normalized["close"].diff()
        normalized["pct_chg"] = normalized["close"].pct_change() * 100
        normalized["preclose"] = normalized["close"].shift(1)
        normalized["volume"] = None
        normalized["turn"] = None
    else:
        raise ValueError(f"不支持的历史数据源: {source}")

    required_columns = ["trade_date", "open", "high", "low", "close", "change", "pct_chg", "volume", "amount", "preclose", "turn"]
    for col in required_columns:
        if col not in normalized.columns:
            normalized[col] = None
    return normalized.sort_values("trade_date").reset_index(drop=True)


def _to_tx_stock_symbol(stock_code):
    code = str(stock_code).strip()
    if code.startswith(("sh", "sz")):
        return code
    if code.startswith(("6", "9")):
        return f"sh{code}"
    return f"sz{code}"


def get_index_history(index_key, start_date, end_date):
    symbol = index_key
    start_dt = pd.to_datetime(start_date, format="%Y%m%d")
    end_dt = pd.to_datetime(end_date, format="%Y%m%d")
    datalen = max(60, min((end_dt - start_dt).days + 20, 1023))
    url = "https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData"
    response = requests.get(
        url,
        params={
            "symbol": symbol,
            "scale": "240",
            "ma": "no",
            "datalen": str(datalen),
        },
        headers=SINA_HEADERS,
        timeout=10,
    )
    response.encoding = "utf-8"
    payload = response.text.strip()
    if not payload:
        raise RuntimeError(f"未获取到指数 {index_key} 数据")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"新浪指数数据解析失败：{exc}") from exc

    df = pd.DataFrame(data)
    if df.empty:
        raise RuntimeError(f"未获取到指数 {index_key} 数据")

    df["trade_date"] = pd.to_datetime(df["day"])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    amount_source = None
    for candidate in ["amount", "Amount", "成交额", "turnover"]:
        if candidate in df.columns:
            amount_source = candidate
            break
    if amount_source:
        df["amount"] = pd.to_numeric(df[amount_source], errors="coerce")
    else:
        df["amount"] = None
    df["change"] = df["close"].diff()
    df["pct_chg"] = df["close"].pct_change() * 100
    df = df[(df["trade_date"] >= start_dt) & (df["trade_date"] <= end_dt)].reset_index(drop=True)
    return df


def get_index_intraday(index_key):
    url = "https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData"
    response = requests.get(
        url,
        params={
            "symbol": index_key,
            "scale": "5",
            "ma": "no",
            "datalen": "96",
        },
        headers=SINA_HEADERS,
        timeout=10,
    )
    response.encoding = "utf-8"
    payload = response.text.strip()
    if not payload:
        raise RuntimeError(f"未获取到指数 {index_key} 分时数据")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"新浪指数分时数据解析失败：{exc}") from exc

    df = pd.DataFrame(data)
    if df.empty:
        raise RuntimeError(f"未获取到指数 {index_key} 分时数据")

    df["trade_date"] = pd.to_datetime(df["day"])
    today = pd.Timestamp(datetime.now().date())
    df = df[df["trade_date"].dt.normalize() == today].reset_index(drop=True)
    if df.empty:
        raise RuntimeError(f"指数 {index_key} 当天暂无分时数据")

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    amount_source = None
    for candidate in ["amount", "Amount", "成交额", "turnover"]:
        if candidate in df.columns:
            amount_source = candidate
            break
    if amount_source:
        df["amount"] = pd.to_numeric(df[amount_source], errors="coerce")
    else:
        df["amount"] = None
    df["change"] = df["close"].diff()
    df["pct_chg"] = df["close"].pct_change() * 100
    return df


def get_index_realtime_snapshots(index_keys):
    """Fetch realtime index snapshots from Sina."""
    if not index_keys:
        return pd.DataFrame(columns=["key"])

    normalized_keys = [str(index_key).strip() for index_key in index_keys if str(index_key).strip()]
    sina_symbols = ",".join(f"s_{index_key}" for index_key in normalized_keys)
    response = requests.get(
        f"http://hq.sinajs.cn/list={sina_symbols}",
        headers=SINA_HEADERS,
        timeout=10,
    )
    response.encoding = "gbk"

    rows = []
    for line in response.text.splitlines():
        if "=" not in line:
            continue

        prefix, payload = line.split("=", 1)
        symbol = prefix.split("hq_str_")[-1].strip()
        raw_values = payload.strip().strip(";").strip('"')
        if not raw_values:
            continue

        values = [item.strip() for item in raw_values.split(",")]
        if len(values) < 4 or not values[0]:
            continue

        key = symbol[2:] if symbol.startswith("s_") else symbol
        latest_price = _to_float(values[1] if len(values) > 1 else None)
        change_amount = _to_float(values[2] if len(values) > 2 else None)
        change_percent = _to_float(values[3] if len(values) > 3 else None)
        volume = _to_float(values[4] if len(values) > 4 else None)
        amount = _to_float(values[5] if len(values) > 5 else None)
        rows.append(
            {
                "key": key,
                "name": values[0],
                "trade_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "latest_price": latest_price,
                "change_amount": change_amount,
                "change_percent": change_percent,
                "volume": volume,
                "amount": amount,
            }
        )

    return pd.DataFrame(rows)


def get_industry_directory():
    data = _sina_request_json(
        "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes"
    )
    rows = []
    _flatten_sina_nodes(data, rows)
    if not rows:
        raise ValueError("未获取到新浪板块列表")

    grouped = {}
    for item in rows:
        code = item["sector_code"]
        name = item["sector_name"]
        if not _is_valid_sina_sector_node(code, name):
            continue
        grouped.setdefault(name, []).append(code)

    records = []
    for name, codes in grouped.items():
        records.append(
            {
                "板块名称": name,
                "板块代码": _select_preferred_sector_code(name, codes),
            }
        )

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError("未获取到新浪板块列表")
    return df.sort_values("板块名称").reset_index(drop=True)


def get_industry_constituents(industry_name, sector_code=None, page=1, page_size=10, sort="symbol", asc="1"):
    resolved_code = _resolve_sector_code(industry_name, sector_code)
    total = _get_sector_stock_count(resolved_code)
    page = max(1, int(page))
    page_size = max(1, min(int(page_size), 100))
    total_pages = max(1, (total + page_size - 1) // page_size) if total else 1
    page = min(page, total_pages)

    data = _sina_request_json(
        "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData",
        params={
            "page": page,
            "num": page_size,
            "sort": str(sort or "symbol"),
            "asc": str(asc or "1"),
            "node": resolved_code,
            "symbol": "",
            "_s_r_a": "page",
        },
    )
    df = pd.DataFrame(data or [])
    if df.empty:
        return {
            "sector_code": resolved_code,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "items": pd.DataFrame(columns=["代码", "名称", "industry", "market", "trade_date", "最新价", "涨跌幅", "涨跌额", "换手率", "成交量", "成交额", "市盈率-动态", "市净率", "总市值"]),
        }

    rename_map = {
        "code": "代码",
        "name": "名称",
        "trade": "最新价",
        "changepercent": "涨跌幅",
        "pricechange": "涨跌额",
        "turnoverratio": "换手率",
        "volume": "成交量",
        "amount": "成交额",
        "per": "市盈率-动态",
        "pb": "市净率",
        "mktcap": "总市值",
        "ticktime": "trade_time",
    }
    df = df.rename(columns={col: rename_map[col] for col in df.columns if col in rename_map}).copy()
    df["代码"] = df["代码"].astype(str).str.strip()
    df["名称"] = df["名称"].astype(str).str.strip()
    df["industry"] = str(industry_name).strip()
    df["market"] = df["代码"].map(_infer_market)
    trade_date = datetime.now().strftime("%Y-%m-%d")
    if "trade_time" in df.columns:
        df["trade_date"] = df["trade_time"].astype(str).apply(lambda value: f"{trade_date} {value}".strip())
    else:
        df["trade_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "sector_code": resolved_code,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "items": df,
    }


def get_stock_directory_snapshot(trade_date=None):
    df = ak.stock_info_a_code_name()
    if df is None or df.empty:
        raise ValueError("未获取到A股股票列表")

    df = df.copy()
    code_column = "code" if "code" in df.columns else "代码"
    name_column = "name" if "name" in df.columns else "名称"
    df["代码"] = df[code_column].astype(str).str.strip()
    df["名称"] = df[name_column].astype(str).str.strip()
    df["market"] = df["代码"].map(_infer_market)
    df["industry"] = ""
    df["trade_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df["最新价"] = None
    df["涨跌幅"] = None
    df["涨跌额"] = None
    df["换手率"] = None
    df["成交量"] = None
    df["成交额"] = None
    return df[["代码", "名称", "market", "industry", "trade_date", "最新价", "涨跌幅", "涨跌额", "换手率", "成交量", "成交额"]]


def get_stock_snapshots(stock_codes):
    if not stock_codes:
        return pd.DataFrame(columns=["code"])

    normalized_codes = [str(code).strip() for code in stock_codes if str(code).strip()]
    sina_symbols = ",".join(f"{_infer_market(code).lower()}{code}" for code in normalized_codes)
    response = requests.get(
        f"http://hq.sinajs.cn/list={sina_symbols}",
        headers=SINA_HEADERS,
        timeout=10,
    )
    response.encoding = "gbk"

    rows = []
    for line in response.text.splitlines():
        if "=" not in line:
            continue

        prefix, payload = line.split("=", 1)
        symbol = prefix.split("hq_str_")[-1].strip()
        raw_values = payload.strip().strip(";").strip('"')
        if not raw_values:
            continue

        values = raw_values.split(",")
        if len(values) < 32 or not values[0]:
            continue

        code = symbol[2:]
        latest_price = _to_float(values[3])
        previous_close = _to_float(values[2])
        rows.append(
            {
                "code": code,
                "trade_date": f"{values[30]} {values[31]}".strip(),
                "latest_price": latest_price,
                "change_amount": None if latest_price is None or previous_close is None else latest_price - previous_close,
                "change_percent": None if latest_price is None or previous_close in (None, 0) else (latest_price - previous_close) / previous_close * 100,
                "turnover_rate": None,
                "volume": _to_float(values[8]),
                "amount": _to_float(values[9]),
            }
        )

    return pd.DataFrame(rows)


def get_full_market_snapshots():
    df = ak.stock_zh_a_spot_em()
    return _normalize_full_market_snapshot_df(df, source_name="eastmoney")


def get_full_market_snapshots_fallback():
    df = ak.stock_zh_a_spot()
    return _normalize_full_market_snapshot_df(df, source_name="akshare")


def get_market_rankings_sina(limit=10):
    page_size = max(5, min(int(limit or 10), 30))
    gainers_df = _fetch_sina_market_rank_page(page_size=page_size, asc="0")
    losers_df = _fetch_sina_market_rank_page(page_size=page_size, asc="1")
    return {
        "gainers": gainers_df.reset_index(drop=True),
        "losers": losers_df.reset_index(drop=True),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _fetch_sina_market_rank_page(page_size=10, asc="0"):
    data = _sina_request_json(
        "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData",
        params={
            "page": 1,
            "num": page_size,
            "sort": "changepercent",
            "asc": str(asc),
            "node": "hs_a",
            "symbol": "",
            "_s_r_a": "page",
        },
    )
    df = pd.DataFrame(data or [])
    if df.empty:
        raise ValueError("新浪涨跌榜数据为空")

    rename_map = {
        "code": "code",
        "name": "name",
        "trade": "latest_price",
        "changepercent": "change_percent",
        "pricechange": "change_amount",
        "turnoverratio": "turnover_rate",
        "volume": "volume",
        "amount": "amount",
        "ticktime": "trade_time",
    }
    working_df = df.rename(columns={col: rename_map[col] for col in df.columns if col in rename_map}).copy()
    if "code" not in working_df.columns or "name" not in working_df.columns:
        raise ValueError("新浪涨跌榜字段异常")

    working_df["code"] = working_df["code"].astype(str).str.strip()
    working_df["name"] = working_df["name"].astype(str).str.strip()
    working_df["industry"] = ""
    working_df["market"] = working_df["code"].map(_infer_market)
    trade_date = datetime.now().strftime("%Y-%m-%d")
    if "trade_time" in working_df.columns:
        working_df["trade_date"] = working_df["trade_time"].astype(str).apply(lambda value: f"{trade_date} {value}".strip())
    else:
        working_df["trade_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for col in ["latest_price", "change_percent", "change_amount", "turnover_rate", "volume", "amount"]:
        if col in working_df.columns:
            working_df[col] = pd.to_numeric(working_df[col], errors="coerce")
        else:
            working_df[col] = None

    return working_df[
        ["code", "name", "industry", "market", "trade_date", "latest_price", "change_percent", "change_amount", "turnover_rate", "volume", "amount"]
    ].drop_duplicates(subset=["code"]).reset_index(drop=True)


def get_full_market_snapshots_sina():
    total = _get_sector_stock_count("hs_a")
    if total <= 0:
        raise ValueError("新浪全市场快照股票总数为空")

    page_size = 200
    total_pages = max(1, (int(total) + page_size - 1) // page_size)
    frames = []
    for page in range(1, total_pages + 1):
        data = _sina_request_json(
            "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData",
            params={
                "page": page,
                "num": page_size,
                "sort": "symbol",
                "asc": "1",
                "node": "hs_a",
                "symbol": "",
                "_s_r_a": "page",
            },
        )
        df = pd.DataFrame(data or [])
        if df.empty:
            continue
        frames.append(df)
        time.sleep(0.12)

    if not frames:
        raise ValueError("新浪全市场快照为空")

    merged_df = pd.concat(frames, ignore_index=True)
    return _normalize_full_market_snapshot_df(merged_df, source_name="sina")


def _normalize_full_market_snapshot_df(df, source_name="unknown"):
    if df is None or df.empty:
        raise ValueError(f"未获取到全市场实时快照，source={source_name}")

    rename_map = {
        "代码": "code",
        "symbol": "code",
        "证券代码": "code",
        "名称": "name",
        "name": "name",
        "证券简称": "name",
        "最新价": "latest_price",
        "trade": "latest_price",
        "最新": "latest_price",
        "涨跌幅": "change_percent",
        "changepercent": "change_percent",
        "涨跌额": "change_amount",
        "pricechange": "change_amount",
        "成交量": "volume",
        "volume": "volume",
        "成交额": "amount",
        "amount": "amount",
        "换手率": "turnover_rate",
        "turnoverratio": "turnover_rate",
        "所属行业": "industry",
        "industry": "industry",
    }
    working_df = df.rename(columns={col: rename_map[col] for col in df.columns if col in rename_map}).copy()
    if "code" not in working_df.columns or "name" not in working_df.columns:
        raise ValueError(f"全市场实时快照字段异常，source={source_name}")

    working_df["code"] = working_df["code"].astype(str).str.strip()
    working_df["name"] = working_df["name"].astype(str).str.strip()
    working_df["market"] = working_df["code"].map(_infer_market)
    working_df["trade_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for col in ["latest_price", "change_percent", "change_amount", "volume", "amount", "turnover_rate"]:
        if col in working_df.columns:
            working_df[col] = pd.to_numeric(working_df[col], errors="coerce")
        else:
            working_df[col] = None
    if "industry" not in working_df.columns:
        working_df["industry"] = ""
    return working_df[
        ["code", "name", "industry", "market", "trade_date", "latest_price", "change_percent", "change_amount", "turnover_rate", "volume", "amount"]
    ].drop_duplicates(subset=["code"]).reset_index(drop=True)


def _infer_market(code):
    code = str(code)
    if code.startswith(("600", "601", "603", "605", "688", "900")):
        return "SH"
    if code.startswith(("430", "440", "830", "870", "920")) or code.startswith(("4", "8")):
        return "BJ"
    return "SZ"


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sina_request_json(url, params=None):
    response = requests.get(url, params=params, headers=SINA_HEADERS, timeout=12)
    response.encoding = "utf-8"
    payload = response.text.strip()
    if not payload:
        return []
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"新浪接口返回解析失败：{exc}") from exc


def _flatten_sina_nodes(node, rows):
    if isinstance(node, list):
        if len(node) >= 3 and isinstance(node[0], str) and isinstance(node[2], str) and node[2]:
            rows.append({"sector_name": node[0], "sector_code": node[2]})
        for item in node:
            _flatten_sina_nodes(item, rows)


def _is_valid_sina_sector_node(code, name):
    if not code or not name:
        return False
    if code.startswith("hk_"):
        return False
    if code in {"sinahy", "swhy", "sw1_hy", "sw2_hy", "sw3_hy"}:
        return False
    return code.startswith(("new_", "sw", "chgn_", "gn_"))


def _select_preferred_sector_code(name, codes):
    if name in SINA_SECTOR_OVERRIDES:
        return SINA_SECTOR_OVERRIDES[name]
    priority_prefixes = ["sw2_", "sw1_", "sw_", "chgn_", "new_", "gn_"]
    for prefix in priority_prefixes:
        for code in codes:
            if code.startswith(prefix):
                return code
    return codes[0]


def _resolve_sector_code(industry_name, sector_code=None):
    if sector_code:
        return str(sector_code).strip()

    directory_df = get_industry_directory()
    matched = directory_df[directory_df["板块名称"].astype(str).str.strip() == str(industry_name).strip()]
    if matched.empty:
        raise ValueError(f"未找到板块 {industry_name} 对应的新浪节点")
    return matched.iloc[0]["板块代码"]


def _get_sector_stock_count(sector_code):
    response = requests.get(
        "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeStockCount",
        params={"node": sector_code},
        headers=SINA_HEADERS,
        timeout=12,
    )
    payload = response.text.strip()
    if not payload:
        return 0
    try:
        cleaned = payload.strip().strip('"').strip("'")
        return int(float(cleaned))
    except ValueError:
        return 0
