from process.common import build_case_result, latest_valid, round_value


def run_case(df, predict_days=1):
    working_df = df.copy()
    working_df["ma5"] = working_df["close"].rolling(5).mean()
    working_df["ma10"] = working_df["close"].rolling(10).mean()
    working_df["ma20"] = working_df["close"].rolling(20).mean()

    latest_close = latest_valid(working_df["close"])
    ma5 = latest_valid(working_df["ma5"])
    ma10 = latest_valid(working_df["ma10"])
    ma20 = latest_valid(working_df["ma20"])

    signal = "neutral"
    score = 0
    if latest_close and ma5 and ma10 and ma20:
        if latest_close > ma5 > ma10 > ma20:
            signal = "bullish"
            score = 2
        elif latest_close < ma5 < ma10 < ma20:
            signal = "bearish"
            score = -2
        elif latest_close > ma20 and ma5 > ma10:
            signal = "bullish"
            score = 1
        elif latest_close < ma20 and ma5 < ma10:
            signal = "bearish"
            score = -1

    summary = (
        f"收盘价 {round_value(latest_close, 2)}，MA5/MA10/MA20 为 "
        f"{round_value(ma5, 2)}/{round_value(ma10, 2)}/{round_value(ma20, 2)}，"
        f"均线结构判断为{signal}。"
    )

    return build_case_result(
        "ma",
        "MA 均线结构",
        signal,
        score,
        summary,
        {
            "predict_days": predict_days,
            "latest_close": round_value(latest_close, 2),
            "ma5": round_value(ma5, 2),
            "ma10": round_value(ma10, 2),
            "ma20": round_value(ma20, 2),
        },
    )
