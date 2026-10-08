from process.common import build_case_result, latest_valid, round_value


def run_case(df, predict_days=1):
    working_df = df.copy()
    working_df["bb_mid"] = working_df["close"].rolling(20).mean()
    rolling_std = working_df["close"].rolling(20).std()
    working_df["bb_upper"] = working_df["bb_mid"] + 2 * rolling_std
    working_df["bb_lower"] = working_df["bb_mid"] - 2 * rolling_std

    latest_close = latest_valid(working_df["close"])
    bb_mid = latest_valid(working_df["bb_mid"])
    bb_upper = latest_valid(working_df["bb_upper"])
    bb_lower = latest_valid(working_df["bb_lower"])

    signal = "neutral"
    score = 0
    if latest_close is not None and bb_upper is not None and bb_lower is not None and bb_mid is not None:
        if latest_close > bb_upper:
            signal = "bearish"
            score = -1
        elif latest_close < bb_lower:
            signal = "bullish"
            score = 1
        elif latest_close > bb_mid:
            signal = "bullish"
            score = 1
        elif latest_close < bb_mid:
            signal = "bearish"
            score = -1

    summary = (
        f"布林带上轨/中轨/下轨为 {round_value(bb_upper, 2)}/{round_value(bb_mid, 2)}/{round_value(bb_lower, 2)}，"
        f"收盘价 {round_value(latest_close, 2)}，布林带判断为{signal}。"
    )
    return build_case_result(
        "bollinger_bands",
        "Bollinger Bands 布林带",
        signal,
        score,
        summary,
        {
            "predict_days": predict_days,
            "latest_close": round_value(latest_close, 2),
            "bb_upper": round_value(bb_upper, 2),
            "bb_mid": round_value(bb_mid, 2),
            "bb_lower": round_value(bb_lower, 2),
        },
    )
