from process.common import build_case_result, latest_valid, round_value


def run_case(df, predict_days=1):
    working_df = df.copy()
    delta = working_df["close"].diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss.replace(0, None)
    working_df["rsi14"] = 100 - (100 / (1 + rs))

    rsi14 = latest_valid(working_df["rsi14"])
    signal = "neutral"
    score = 0
    if rsi14 is not None:
        if rsi14 >= 70:
            signal = "bearish"
            score = -1
        elif rsi14 <= 30:
            signal = "bullish"
            score = 1

    summary = f"RSI14 当前为 {round_value(rsi14, 2)}，处于{'超买' if signal == 'bearish' else '超卖' if signal == 'bullish' else '中性'}区间。"
    return build_case_result(
        "rsi",
        "RSI 强弱指标",
        signal,
        score,
        summary,
        {
            "predict_days": predict_days,
            "rsi14": round_value(rsi14, 2),
            "overbought_threshold": 70,
            "oversold_threshold": 30,
        },
    )
