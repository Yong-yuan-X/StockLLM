import math

import pandas as pd


def latest_valid(series, default=None):
    cleaned = pd.Series(series).dropna()
    if cleaned.empty:
        return default
    return float(cleaned.iloc[-1])


def round_value(value, digits=4):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return round(float(value), digits)


def price_change_pct(base_value, target_value):
    if base_value in (None, 0) or target_value is None:
        return None
    return (float(target_value) - float(base_value)) / float(base_value) * 100


def build_case_result(case_id, title, signal, score, summary, details):
    return {
        "case": case_id,
        "title": title,
        "signal": signal,
        "score": score,
        "summary": summary,
        "details": details,
    }
