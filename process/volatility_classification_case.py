import math

from process.common import build_case_result, round_value


def _safe_std(values):
    cleaned = [float(value) for value in values if value is not None]
    if len(cleaned) < 2:
        return None
    mean_value = sum(cleaned) / len(cleaned)
    variance = sum((value - mean_value) ** 2 for value in cleaned) / (len(cleaned) - 1)
    return math.sqrt(variance)


def _percentile_rank(values, target):
    cleaned = sorted(float(value) for value in values if value is not None)
    if not cleaned:
        return None
    smaller_or_equal = len([value for value in cleaned if value <= target])
    return smaller_or_equal / len(cleaned)


def run_case(df, predict_days=1):
    working_df = df.copy()
    working_df["daily_return"] = working_df["close"].pct_change()
    rolling_volatility = working_df["daily_return"].rolling(20).apply(_safe_std, raw=False) * math.sqrt(252) * 100

    latest_volatility = rolling_volatility.dropna().iloc[-1] if not rolling_volatility.dropna().empty else None
    lookback_volatility = rolling_volatility.dropna().tail(120).tolist()
    volatility_rank = _percentile_rank(lookback_volatility, latest_volatility) if latest_volatility is not None else None

    latest_close = float(working_df["close"].iloc[-1]) if not working_df.empty else None
    close_20 = float(working_df["close"].iloc[-21]) if len(working_df) > 20 else None
    trend_20d = ((latest_close - close_20) / close_20 * 100) if latest_close and close_20 else None

    regime = "medium"
    signal = "neutral"
    score = 0
    if volatility_rank is not None:
        if volatility_rank <= 0.33:
            regime = "low"
        elif volatility_rank >= 0.67:
            regime = "high"

        if regime == "low" and trend_20d is not None and trend_20d > 0:
            signal = "bullish"
            score = 1
        elif regime == "high" and trend_20d is not None and trend_20d < 0:
            signal = "bearish"
            score = -2
        elif regime == "high":
            signal = "neutral"
            score = -1
        elif regime == "medium" and trend_20d is not None and trend_20d > 0:
            signal = "bullish"
            score = 1
        elif regime == "medium" and trend_20d is not None and trend_20d < 0:
            signal = "bearish"
            score = -1

    summary = (
        f"20日年化波动率约为 {round_value(latest_volatility, 2)}%，"
        f"处于近 120 个交易日的 {round_value((volatility_rank or 0) * 100, 2)} 分位，"
        f"当前波动状态为 {regime}，结合近20日趋势判断为{signal}。"
    )
    return build_case_result(
        "volatility_classification",
        "波动率分类",
        signal,
        score,
        summary,
        {
            "predict_days": predict_days,
            "volatility_window": 20,
            "latest_annualized_volatility_pct": round_value(latest_volatility, 2),
            "volatility_percentile": round_value((volatility_rank or 0) * 100, 2),
            "volatility_regime": regime,
            "trend_20d_pct": round_value(trend_20d, 2),
        },
    )
