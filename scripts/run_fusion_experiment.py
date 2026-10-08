#!/usr/bin/env python3
import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import API_CACHE_DIR, DATABASE  # noqa: E402
from core.services.analysis_service import AVAILABLE_CASES, DEFAULT_CASE_ORDER, _build_overall_signal  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser(description="基于本地 stock_daily_history 表运行多模型融合实验")
    parser.add_argument("--database", default=str(PROJECT_ROOT / DATABASE), help="SQLite 数据库路径")
    parser.add_argument("--sample-size", type=int, default=1000, help="实验样本数")
    parser.add_argument("--cutoff-date", default="2026-04-01", help="用于预测的截止日期，格式 YYYY-MM-DD")
    parser.add_argument("--actual-date", default="2026-04-08", help="用于对比的实际日期，格式 YYYY-MM-DD")
    parser.add_argument("--predict-days", type=int, default=4, help="预测步长")
    parser.add_argument("--neutral-threshold-pct", type=float, default=2.0, help="当绝对涨跌幅不超过该阈值时记为 neutral")
    parser.add_argument("--min-history-rows", type=int, default=120, help="最少历史样本行数")
    parser.add_argument("--progress-step", type=int, default=50, help="每处理多少支股票打印一次进度")
    parser.add_argument("--output-json", default="", help="实验汇总 JSON 输出路径")
    parser.add_argument("--output-csv", default="", help="逐股票结果 CSV 输出路径")
    return parser.parse_args()


def default_output_json():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return API_CACHE_DIR / f"fusion_experiment_{timestamp}.json"


def default_output_csv():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return API_CACHE_DIR / f"fusion_experiment_{timestamp}.csv"


def load_excluded_codes(conn):
    rows = conn.execute("SELECT DISTINCT stock_code FROM user_stocks").fetchall()
    return {str(row[0]).zfill(6) for row in rows}


def load_eligible_samples(conn, excluded_codes, cutoff_date, actual_date, sample_size):
    placeholders = ",".join(["?"] * len(excluded_codes)) if excluded_codes else "''"
    sql = f"""
        SELECT stock_code, MAX(stock_name) as stock_name
        FROM stock_daily_history
        WHERE stock_code NOT IN ({placeholders})
          AND trade_date IN (?, ?)
        GROUP BY stock_code
        HAVING COUNT(DISTINCT trade_date) = 2
        ORDER BY stock_code
        LIMIT ?
    """
    params = [*sorted(excluded_codes), cutoff_date, actual_date, sample_size]
    return pd.read_sql_query(sql, conn, params=params)


def load_history_df(conn, stock_code, cutoff_date):
    df = pd.read_sql_query(
        """
        SELECT trade_date, open, high, low, close, preclose, change, pct_chg, volume, amount, turn
        FROM stock_daily_history
        WHERE stock_code = ? AND trade_date <= ?
        ORDER BY trade_date
        """,
        conn,
        params=[stock_code, cutoff_date],
    )
    if df.empty:
        return df
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    for col in ["open", "high", "low", "close", "preclose", "change", "pct_chg", "volume", "amount", "turn"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_actual_close(conn, stock_code, actual_date):
    row = conn.execute(
        "SELECT close FROM stock_daily_history WHERE stock_code = ? AND trade_date = ? LIMIT 1",
        (stock_code, actual_date),
    ).fetchone()
    return None if row is None else float(row[0])


def signal_from_close(base_close, actual_close, neutral_threshold_pct):
    return_pct = (actual_close - base_close) / base_close * 100 if base_close else 0
    if abs(return_pct) <= neutral_threshold_pct:
        return "neutral"
    if actual_close > base_close:
        return "bullish"
    return "bearish"


def bin_from_score(score):
    if score < 0.3:
        return "0.00-0.30"
    if score <= 0.7:
        return "0.30-0.70"
    return "0.70-1.00"


def main():
    args = parse_args()
    db_path = Path(args.database)
    output_json = Path(args.output_json) if args.output_json else default_output_json()
    output_csv = Path(args.output_csv) if args.output_csv else default_output_csv()
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    excluded_codes = load_excluded_codes(conn)
    samples = load_eligible_samples(conn, excluded_codes, args.cutoff_date, args.actual_date, args.sample_size)

    print(f"实验样本目标数: {args.sample_size}", flush=True)
    print(f"实际可用样本数: {len(samples)}", flush=True)
    print(f"截止日期: {args.cutoff_date}", flush=True)
    print(f"对比日期: {args.actual_date}", flush=True)
    print(f"预测步长: {args.predict_days}", flush=True)
    print(f"震荡阈值: |return| <= {args.neutral_threshold_pct}%", flush=True)

    risk_modes = ["conservative", "balanced", "aggressive"]
    mode_summary = {
        m: {
            "total": 0,
            "correct": 0,
            "bullish_pred": 0,
            "bearish_pred": 0,
            "neutral_pred": 0,
            "bins": {
                "0.00-0.30": [0, 0],
                "0.30-0.70": [0, 0],
                "0.70-1.00": [0, 0],
            },
        }
        for m in risk_modes
    }
    actual_counts = {"bullish": 0, "bearish": 0, "neutral": 0}
    rows = []
    start = time.time()

    for idx, row in samples.iterrows():
        stock_code = str(row["stock_code"]).zfill(6)
        stock_name = str(row["stock_name"] or "").strip()
        history_df = load_history_df(conn, stock_code, args.cutoff_date)
        if len(history_df) < args.min_history_rows:
            continue

        actual_close = load_actual_close(conn, stock_code, args.actual_date)
        if actual_close is None:
            continue

        base_close = float(history_df.iloc[-1]["close"])
        actual_signal = signal_from_close(base_close, actual_close, args.neutral_threshold_pct)
        actual_counts[actual_signal] += 1

        case_results = []
        for case_key in DEFAULT_CASE_ORDER:
            case_results.append(AVAILABLE_CASES[case_key]["runner"](history_df, predict_days=args.predict_days))

        row_record = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "base_close": round(base_close, 2),
            "actual_close": round(actual_close, 2),
            "actual_signal": actual_signal,
            "actual_return_pct": round((actual_close - base_close) / base_close * 100, 2),
        }

        for mode in risk_modes:
            aggregate = _build_overall_signal(case_results, risk_preference=mode)
            pred = aggregate["overall_signal"]
            score = float(aggregate["weighted_fusion_score"])
            correct = int(pred == actual_signal)
            bin_key = bin_from_score(score)
            summary = mode_summary[mode]
            summary["total"] += 1
            summary["correct"] += correct
            summary[f"{pred}_pred"] += 1
            summary["bins"][bin_key][0] += 1
            summary["bins"][bin_key][1] += correct

            row_record[f"{mode}_signal"] = pred
            row_record[f"{mode}_score"] = round(score, 4)
            row_record[f"{mode}_bin"] = bin_key
            row_record[f"{mode}_correct"] = bool(correct)

        rows.append(row_record)
        if (idx + 1) % args.progress_step == 0:
            print(f"processed={idx + 1}", flush=True)

    conn.close()

    summary_out = {}
    for mode, item in mode_summary.items():
        total = item["total"] or 1
        summary_out[mode] = {
            "total": item["total"],
            "correct": item["correct"],
            "accuracy": round(item["correct"] / total * 100, 2),
            "bullish_pred": item["bullish_pred"],
            "bearish_pred": item["bearish_pred"],
            "neutral_pred": item["neutral_pred"],
            "bins": {
                k: {
                    "samples": v[0],
                    "correct": v[1],
                    "accuracy": round(v[1] / v[0] * 100, 2) if v[0] else None,
                }
                for k, v in item["bins"].items()
            },
        }

    payload = {
        "sample_count": len(rows),
        "excluded_codes": sorted(excluded_codes),
        "cutoff_date": args.cutoff_date,
        "actual_date": args.actual_date,
        "predict_days": args.predict_days,
        "neutral_threshold_pct": args.neutral_threshold_pct,
        "actual_counts": actual_counts,
        "summary": summary_out,
        "elapsed_seconds": round(time.time() - start, 2),
    }

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    pd.DataFrame(rows).to_csv(output_csv, index=False, encoding="utf-8-sig")

    print("\n实验完成", flush=True)
    print(f"最终样本数: {len(rows)}", flush=True)
    print(f"结果 JSON: {output_json}", flush=True)
    print(f"结果 CSV: {output_csv}", flush=True)
    print(json.dumps(payload, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
