from process.common import build_case_result, round_value


def _slope(values):
    if len(values) < 2:
        return 0
    start = float(values[0])
    end = float(values[-1])
    if start == 0:
        return 0
    return (end - start) / start * 100


def run_case(df, predict_days=1):
    working_df = df.copy()
    close_values = working_df["close"].dropna().tolist()
    recent_20 = close_values[-20:] if len(close_values) >= 20 else close_values
    recent_60 = close_values[-60:] if len(close_values) >= 60 else close_values

    slope_20 = _slope(recent_20)
    slope_60 = _slope(recent_60)
    latest_close = float(close_values[-1]) if close_values else None
    recent_high = max(recent_20) if recent_20 else None
    recent_low = min(recent_20) if recent_20 else None

    signal = "neutral"
    score = 0
    if slope_20 > 5 and slope_60 > 8:
        signal = "bullish"
        score = 2
    elif slope_20 < -5 and slope_60 < -8:
        signal = "bearish"
        score = -2
    elif slope_20 > 0 and slope_60 > 0:
        signal = "bullish"
        score = 1
    elif slope_20 < 0 and slope_60 < 0:
        signal = "bearish"
        score = -1

    summary = (
        f"近20日趋势 {round_value(slope_20, 2)}%，近60日趋势 {round_value(slope_60, 2)}%，"
        f"当前走势判断为{signal}。"
    )
    return build_case_result(
        "trend",
        "趋势判断",
        signal,
        score,
        summary,
        {
            "predict_days": predict_days,
            "latest_close": round_value(latest_close, 2),
            "slope_20_pct": round_value(slope_20, 2),
            "slope_60_pct": round_value(slope_60, 2),
            "recent_20_high": round_value(recent_high, 2),
            "recent_20_low": round_value(recent_low, 2),
        },
    )
