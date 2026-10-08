from process.common import build_case_result, latest_valid, round_value


def run_case(df, predict_days=1):
    working_df = df.copy()
    ema12 = working_df["close"].ewm(span=12, adjust=False).mean()
    ema26 = working_df["close"].ewm(span=26, adjust=False).mean()
    dif = ema12 - ema26
    dea = dif.ewm(span=9, adjust=False).mean()
    macd_hist = (dif - dea) * 2

    latest_dif = latest_valid(dif)
    latest_dea = latest_valid(dea)
    latest_hist = latest_valid(macd_hist)

    signal = "neutral"
    score = 0
    if latest_dif is not None and latest_dea is not None:
        if latest_dif > latest_dea and (latest_hist or 0) > 0:
            signal = "bullish"
            score = 1
        elif latest_dif < latest_dea and (latest_hist or 0) < 0:
            signal = "bearish"
            score = -1

    summary = (
        f"MACD 当前 DIF/DEA/柱体 为 "
        f"{round_value(latest_dif, 4)}/{round_value(latest_dea, 4)}/{round_value(latest_hist, 4)}，"
        f"趋势偏{signal}。"
    )
    return build_case_result(
        "macd",
        "MACD 动量指标",
        signal,
        score,
        summary,
        {
            "predict_days": predict_days,
            "dif": round_value(latest_dif, 4),
            "dea": round_value(latest_dea, 4),
            "histogram": round_value(latest_hist, 4),
        },
    )
