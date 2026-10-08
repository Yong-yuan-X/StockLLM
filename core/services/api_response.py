import math
from decimal import Decimal

from flask import jsonify


def _sanitize_json_value(value):
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, Decimal):
        numeric_value = float(value)
        return numeric_value if math.isfinite(numeric_value) else None
    if type(value).__name__ in {"NAType", "NaTType"}:
        return None
    if isinstance(value, dict):
        return {str(key): _sanitize_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_sanitize_json_value(item) for item in value]

    item_method = getattr(value, "item", None)
    if callable(item_method):
        try:
            return _sanitize_json_value(item_method())
        except (TypeError, ValueError):
            pass

    try:
        if value != value:
            return None
    except (TypeError, ValueError):
        pass
    return value


def success_response(message, data=None, status=200):
    response = jsonify(_sanitize_json_value({"code": status, "msg": message, "data": data}))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response, status


def error_response(message, status=500, data=None):
    response = jsonify(_sanitize_json_value({"code": status, "msg": message, "data": data}))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response, status
