import os

import requests


_ORIGINAL_SESSION_INIT = requests.Session.__init__
_PATCHED = False


def clear_proxy_environment():
    """Avoid local proxy settings interfering with requests/akshare."""
    proxy_keys = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ]
    for key in proxy_keys:
        os.environ.pop(key, None)

    os.environ["NO_PROXY"] = "*"
    os.environ["no_proxy"] = "*"


def _patched_session_init(self, *args, **kwargs):
    _ORIGINAL_SESSION_INIT(self, *args, **kwargs)
    self.trust_env = False


def configure_requests():
    """Disable proxy inheritance for all requests sessions."""
    global _PATCHED
    clear_proxy_environment()
    if not _PATCHED:
        requests.Session.__init__ = _patched_session_init
        _PATCHED = True
