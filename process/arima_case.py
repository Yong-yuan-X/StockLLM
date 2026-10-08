from process.common import build_case_result, price_change_pct, round_value


def _fit_ar1(diff_values):
    if len(diff_values) < 3:
        return 0.0, 0.0

    x_values = diff_values[:-1]
    y_values = diff_values[1:]
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    phi = numerator / denominator if denominator else 0.0
    intercept = y_mean - phi * x_mean
    return intercept, phi


def _forecast_arima_110(close_values, steps):
    if len(close_values) < 20:
        return None, None

    diff_values = [close_values[index] - close_values[index - 1] for index in range(1, len(close_values))]
    intercept, phi = _fit_ar1(diff_values)

    predicted_close = float(close_values[-1])
    previous_diff = diff_values[-1]
    forecast_diffs = []
    for _ in range(max(1, int(steps))):
        next_diff = intercept + phi * previous_diff
        forecast_diffs.append(next_diff)
        predicted_close += next_diff
        previous_diff = next_diff
    return predicted_close, forecast_diffs


def run_case(df, predict_days=1):
    close_values = df["close"].dropna().tail(160).tolist()
    latest_close = float(close_values[-1]) if close_values else None
    predicted_close, forecast_diffs = _forecast_arima_110(close_values, predict_days)
    predicted_pct = price_change_pct(latest_close, predicted_close)

    signal = "neutral"
    score = 0
    if predicted_pct is not None:
        if predicted_pct >= 1.2:
            signal = "bullish"
            score = 2
        elif predicted_pct <= -1.2:
            signal = "bearish"
            score = -2
        elif predicted_pct > 0:
            signal = "bullish"
            score = 1
        elif predicted_pct < 0:
            signal = "bearish"
            score = -1

    summary = (
        f"基于最近 {len(close_values)} 个交易日的 ARIMA(1,1,0) 近似建模，"
        f"预测 {predict_days} 天后价格约为 {round_value(predicted_close, 2)}，"
        f"相对当前变动 {round_value(predicted_pct, 2)}%。"
    )
    return build_case_result(
        "arima",
        "ARIMA 时序预测",
        signal,
        score,
        summary,
        {
            "predict_days": predict_days,
            "model_order": "ARIMA(1,1,0)",
            "window_size": len(close_values),
            "latest_close": round_value(latest_close, 2),
            "predicted_close": round_value(predicted_close, 2),
            "predicted_change_pct": round_value(predicted_pct, 2),
            "forecast_diffs": [round_value(value, 4) for value in (forecast_diffs or [])],
        },
    )
