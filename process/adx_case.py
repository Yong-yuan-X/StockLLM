from process.common import build_case_result, latest_valid, round_value


def run_case(df, predict_days=1):
    working_df = df.copy()

    high_diff = working_df["high"].diff()
    low_diff = -working_df["low"].diff()
    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0.0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0.0)

    prev_close = working_df["close"].shift(1)
    tr_components = [
        working_df["high"] - working_df["low"],
        (working_df["high"] - prev_close).abs(),
        (working_df["low"] - prev_close).abs(),
    ]
    true_range = tr_components[0].combine(tr_components[1], max).combine(tr_components[2], max)

    atr = true_range.rolling(14).mean()
    plus_di = 100 * (plus_dm.rolling(14).mean() / atr.replace(0, None))
    minus_di = 100 * (minus_dm.rolling(14).mean() / atr.replace(0, None))
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, None)) * 100
    adx = dx.rolling(14).mean()

    latest_adx = latest_valid(adx)
    latest_plus_di = latest_valid(plus_di)
    latest_minus_di = latest_valid(minus_di)

    signal = "neutral"
    score = 0
    if latest_adx is not None and latest_plus_di is not None and latest_minus_di is not None:
        if latest_adx >= 25 and latest_plus_di > latest_minus_di:
            signal = "bullish"
            score = 2
        elif latest_adx >= 25 and latest_plus_di < latest_minus_di:
            signal = "bearish"
            score = -2
        elif latest_plus_di > latest_minus_di:
            signal = "bullish"
            score = 1
        elif latest_plus_di < latest_minus_di:
            signal = "bearish"
            score = -1

    summary = (
        f"ADX 为 {round_value(latest_adx, 2)}，+DI/-DI 为 "
        f"{round_value(latest_plus_di, 2)}/{round_value(latest_minus_di, 2)}，趋势强度判断为{signal}。"
    )
    return build_case_result(
        "adx",
        "ADX 趋势强度指标",
        signal,
        score,
        summary,
        {
            "predict_days": predict_days,
            "adx": round_value(latest_adx, 2),
            "plus_di": round_value(latest_plus_di, 2),
            "minus_di": round_value(latest_minus_di, 2),
            "trend_threshold": 25,
        },
    )
