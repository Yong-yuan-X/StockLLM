import json
import time
from pathlib import Path


def load_cache(cache_file, max_age_seconds=300):
    path = Path(cache_file)
    if not path.exists():
        return None

    payload = json.loads(path.read_text(encoding="utf-8"))
    if time.time() - payload.get("saved_at", 0) > max_age_seconds:
        return None
    return payload.get("data")


def save_cache(cache_file, data):
    path = Path(cache_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"saved_at": time.time(), "data": data}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
