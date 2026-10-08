import os
from pathlib import Path

from core.app_settings import MAIL_SETTINGS


DATABASE = os.getenv("DATABASE_PATH", "stock.db")
RUNTIME_DIR = Path("runtime")
CACHE_ROOT_DIR = RUNTIME_DIR / "cache"
API_CACHE_DIR = CACHE_ROOT_DIR / "api"
MARKET_INDEX_CACHE_DIR = CACHE_ROOT_DIR / "market_index"
SENTIMENT_CACHE_DIR = CACHE_ROOT_DIR / "sentiment"
STOCK_HISTORY_CACHE_DIR = CACHE_ROOT_DIR / "stock_history"
REPORT_JSON_DIR = CACHE_ROOT_DIR / "reports"
SECTOR_CACHE_FILE = API_CACHE_DIR / "industry_boards.csv"
SECTOR_STOCK_CACHE_DIR = API_CACHE_DIR / "sector_constituents"
STOCK_DIRECTORY_CACHE_FILE = API_CACHE_DIR / "stock_directory.csv"
STOCK_RANKING_CACHE_FILE = API_CACHE_DIR / "stock_rankings.csv"
DEFAULT_SECTORS = ["小金属", "证券", "银行", "半导体", "人工智能"]
FORUM_UPLOAD_DIR = RUNTIME_DIR / "forum_uploads"
USER_AVATAR_DIR = RUNTIME_DIR / "user_avatars"

MAIL_HOST = MAIL_SETTINGS.host
MAIL_PORT = MAIL_SETTINGS.port
MAIL_USERNAME = MAIL_SETTINGS.username
MAIL_PASSWORD = MAIL_SETTINGS.password
MAIL_USE_TLS = MAIL_SETTINGS.use_tls
MAIL_USE_SSL = MAIL_SETTINGS.use_ssl
MAIL_FROM_NAME = MAIL_SETTINGS.from_name
MAIL_FROM_ADDRESS = MAIL_SETTINGS.from_address


def ensure_runtime_directories():
    RUNTIME_DIR.mkdir(exist_ok=True)
    CACHE_ROOT_DIR.mkdir(parents=True, exist_ok=True)
    API_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    MARKET_INDEX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    SENTIMENT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    STOCK_HISTORY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON_DIR.mkdir(parents=True, exist_ok=True)
    SECTOR_STOCK_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FORUM_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    USER_AVATAR_DIR.mkdir(parents=True, exist_ok=True)
