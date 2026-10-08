#!/usr/bin/env python3
import argparse
import csv
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import API_CACHE_DIR, DATABASE, ensure_runtime_directories  # noqa: E402
from data_sources.akshare_provider import get_stock_history  # noqa: E402


TABLE_SQL = """
CREATE TABLE IF NOT EXISTS stock_daily_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,
    stock_name TEXT,
    trade_date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    preclose REAL,
    change REAL,
    pct_chg REAL,
    volume REAL,
    amount REAL,
    turn REAL,
    source TEXT,
    batch_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (stock_code, trade_date)
)
"""

INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_stock_daily_history_code_date
ON stock_daily_history (stock_code, trade_date)
"""


def parse_args():
    yesterday = datetime.now() - timedelta(days=1)
    default_end = yesterday.strftime("%Y%m%d")
    default_start = (yesterday - timedelta(days=365 * 3)).strftime("%Y%m%d")

    parser = argparse.ArgumentParser(description="根据失败清单补跑历史行情写库任务")
    parser.add_argument("failure_csv", help="失败股票清单 CSV 路径")
    parser.add_argument("--start-date", default=default_start, help="开始日期，格式 YYYYMMDD")
    parser.add_argument("--end-date", default=default_end, help="结束日期，格式 YYYYMMDD")
    parser.add_argument("--workers", type=int, default=10, help="并发抓取线程数")
    parser.add_argument("--retry-attempts", type=int, default=2, help="单只股票额外补跑次数")
    parser.add_argument("--database", default=str(PROJECT_ROOT / DATABASE), help="SQLite 数据库路径")
    parser.add_argument("--failure-file", default="", help="补跑后仍失败的清单路径")
    return parser.parse_args()


def ensure_table(conn):
    conn.execute(TABLE_SQL)
    conn.execute(INDEX_SQL)
    conn.commit()


def load_failures(csv_path):
    file_path = Path(csv_path)
    if not file_path.exists():
        raise FileNotFoundError(f"失败清单不存在: {file_path}")

    df = pd.read_csv(file_path, encoding="utf-8-sig")
    if "stock_code" not in df.columns:
        raise ValueError("失败清单缺少 stock_code 列")
    if "stock_name" not in df.columns:
        df["stock_name"] = ""

    df["stock_code"] = df["stock_code"].astype(str).str.strip().str.zfill(6)
    df["stock_name"] = df["stock_name"].astype(str).fillna("").str.strip()
    df = df.drop_duplicates(subset=["stock_code"]).reset_index(drop=True)
    return df[["stock_code", "stock_name"]]


def normalize_history_df(df, stock_code, stock_name):
    working = df.copy()
    working["trade_date"] = pd.to_datetime(working["trade_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    working["stock_code"] = str(stock_code).zfill(6)
    working["stock_name"] = stock_name
    working["source"] = str(df.attrs.get("source", "unknown"))
    working["batch_date"] = datetime.now().strftime("%Y-%m-%d")
    columns = [
        "stock_code",
        "stock_name",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "preclose",
        "change",
        "pct_chg",
        "volume",
        "amount",
        "turn",
        "source",
        "batch_date",
    ]
    for col in columns:
        if col not in working.columns:
            working[col] = None
    working = working[columns].dropna(subset=["trade_date"]).reset_index(drop=True)
    return working


def upsert_history_rows(conn, history_df):
    rows = [
        (
            row["stock_code"],
            row["stock_name"],
            row["trade_date"],
            row["open"],
            row["high"],
            row["low"],
            row["close"],
            row["preclose"],
            row["change"],
            row["pct_chg"],
            row["volume"],
            row["amount"],
            row["turn"],
            row["source"],
            row["batch_date"],
        )
        for _, row in history_df.iterrows()
    ]
    conn.executemany(
        """
        INSERT INTO stock_daily_history (
            stock_code, stock_name, trade_date, open, high, low, close, preclose,
            change, pct_chg, volume, amount, turn, source, batch_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(stock_code, trade_date) DO UPDATE SET
            stock_name=excluded.stock_name,
            open=excluded.open,
            high=excluded.high,
            low=excluded.low,
            close=excluded.close,
            preclose=excluded.preclose,
            change=excluded.change,
            pct_chg=excluded.pct_chg,
            volume=excluded.volume,
            amount=excluded.amount,
            turn=excluded.turn,
            source=excluded.source,
            batch_date=excluded.batch_date,
            updated_at=CURRENT_TIMESTAMP
        """,
        rows,
    )


def resolve_failure_file(custom_path=""):
    if custom_path:
        return Path(custom_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return API_CACHE_DIR / f"retry_failures_{timestamp}.csv"


def write_failure_file(file_path, failures):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["stock_code", "stock_name", "error"])
        for stock_code, stock_name, error in failures:
            writer.writerow([stock_code, stock_name, error])


def fetch_with_retry(stock_code, stock_name, start_date, end_date, retry_attempts):
    last_error = None
    total_attempts = retry_attempts + 1

    for attempt in range(1, total_attempts + 1):
        try:
            history_df = get_stock_history(
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
            )
            normalized_df = normalize_history_df(history_df, stock_code, stock_name)
            return normalized_df, attempt
        except Exception as exc:
            last_error = exc
            if attempt < total_attempts:
                time.sleep(1)

    raise RuntimeError(f"补跑失败（共尝试 {total_attempts} 次）: {last_error}") from last_error


def main():
    args = parse_args()
    ensure_runtime_directories()
    if args.workers < 1:
        raise ValueError("workers 不能小于 1")
    if args.retry_attempts < 0:
        raise ValueError("retry-attempts 不能小于 0")

    db_path = Path(args.database)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    ensure_table(conn)
    failure_file = resolve_failure_file(args.failure_file)

    failures_df = load_failures(args.failure_csv)
    total = len(failures_df)

    print(f"待补跑股票数量: {total}")
    print(f"日期范围: {args.start_date} -> {args.end_date}")
    print(f"数据库文件: {db_path}")
    print(f"并发抓取线程数: {args.workers}")
    print(f"单只股票额外补跑次数: {args.retry_attempts}")
    print(f"输出失败清单: {failure_file}")

    success_count = 0
    fail_count = 0
    total_rows = 0
    failures = []

    future_map = {}
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for idx, row in failures_df.iterrows():
            stock_code = row["stock_code"]
            stock_name = row["stock_name"]
            future = executor.submit(
                fetch_with_retry,
                stock_code,
                stock_name,
                args.start_date,
                args.end_date,
                args.retry_attempts,
            )
            future_map[future] = (idx, stock_code, stock_name)

        for future in as_completed(future_map):
            idx, stock_code, stock_name = future_map[future]
            try:
                normalized_df, used_attempt = future.result()
                upsert_history_rows(conn, normalized_df)
                conn.commit()
                inserted = len(normalized_df)
                total_rows += inserted
                success_count += 1
                print(
                    f"[{idx + 1}/{total}] OK {stock_code} {stock_name} -> "
                    f"{inserted} rows (attempt={used_attempt})"
                )
            except Exception as exc:
                conn.rollback()
                fail_count += 1
                failures.append((stock_code, stock_name, str(exc)))
                print(f"[{idx + 1}/{total}] FAIL {stock_code} {stock_name} -> {exc}")

    conn.close()

    print("\n补跑完成")
    print(f"成功股票数: {success_count}")
    print(f"失败股票数: {fail_count}")
    print(f"写入/更新总行数: {total_rows}")

    if failures:
        write_failure_file(failure_file, failures)
        print(f"\n仍失败股票已写入: {failure_file}")
    else:
        print("\n本次补跑无失败股票，未生成失败清单。")


if __name__ == "__main__":
    main()
