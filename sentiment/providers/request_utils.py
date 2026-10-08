import random
import time

import requests


DEFAULT_TIMEOUT = 15


def sleep_with_jitter(base_seconds=0.0, jitter_seconds=0.0):
    delay = max(0.0, float(base_seconds or 0.0))
    jitter = max(0.0, float(jitter_seconds or 0.0))
    if jitter > 0:
        delay += random.uniform(0, jitter)
    if delay > 0:
        time.sleep(delay)


def request_get_with_retry(url, *, params=None, headers=None, timeout=DEFAULT_TIMEOUT, retries=3, backoff_base=1.0, jitter_seconds=0.4):
    last_error = None
    retries = max(1, int(retries))
    for attempt in range(retries):
        try:
            return requests.get(url, params=params, headers=headers, timeout=timeout)
        except requests.RequestException as exc:
            last_error = exc
            if attempt >= retries - 1:
                break
            sleep_with_jitter(backoff_base * (2 ** attempt), jitter_seconds)
    raise last_error


def call_with_retry(func, *, retries=3, backoff_base=1.0, jitter_seconds=0.4):
    last_error = None
    retries = max(1, int(retries))
    for attempt in range(retries):
        try:
            return func()
        except Exception as exc:
            last_error = exc
            if attempt >= retries - 1:
                break
            sleep_with_jitter(backoff_base * (2 ** attempt), jitter_seconds)
    raise last_error
