from process.common import build_case_result, price_change_pct, round_value


def _linear_regression_predict(values, steps_ahead=1):
    n = len(values)
    if n < 2:
        return None, None, None

    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    numerator = 0.0
    denominator = 0.0
    for index, value in enumerate(values):
        numerator += (index - x_mean) * (value - y_mean)
        denominator += (index - x_mean) ** 2
    slope = numerator / denominator if denominator else 0.0
    intercept = y_mean - slope * x_mean
    prediction_index = n - 1 + max(1, int(steps_ahead))
    predicted = intercept + slope * prediction_index
    return predicted, slope, intercept


def run_case(df, predict_days=1):
    close_values = df["close"].dropna().tail(60).tolist()
    latest_close = float(close_values[-1]) if close_values else None
    predicted_close, slope, intercept = _linear_regression_predict(close_values, predict_days)
    predicted_pct = price_change_pct(latest_close, predicted_close)

    signal = "neutral"
    score = 0
    if predicted_pct is not None:
        if predicted_pct > 1:
            signal = "bullish"
            score = 1
        elif predicted_pct < -1:
            signal = "bearish"
            score = -1

    summary = (
        f"基于最近60个交易日线性回归，预测 {predict_days} 天后价格约为 "
        f"{round_value(predicted_close, 2)}，相对当前变动 {round_value(predicted_pct, 2)}%。"
    )
    return build_case_result(
        "linear_regression",
        "线性回归预测",
        signal,
        score,
        summary,
        {
            "predict_days": predict_days,
            "window_size": len(close_values),
            "latest_close": round_value(latest_close, 2),
            "predicted_close": round_value(predicted_close, 2),
            "predicted_change_pct": round_value(predicted_pct, 2),
            "slope": round_value(slope, 6),
            "intercept": round_value(intercept, 4),
        },
    )
