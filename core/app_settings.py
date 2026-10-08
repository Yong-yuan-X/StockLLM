import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def _load_local_env_file(path=".env"):
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


if load_dotenv:
    load_dotenv()
else:
    _load_local_env_file()


@dataclass(frozen=True)
class AdminSettings:
    username: str
    password: str


@dataclass(frozen=True)
class MailSettings:
    host: str
    port: int
    username: str
    password: str
    use_tls: bool
    use_ssl: bool
    from_name: str
    from_address: str


@dataclass(frozen=True)
class ModelProviderSettings:
    base_url: str
    model: str
    api_key: str


ADMIN_SETTINGS = AdminSettings(
    username=os.getenv("ADMIN_USERNAME", "admin"),
    password=os.getenv("ADMIN_PASSWORD", ""),
)

MAIL_SETTINGS = MailSettings(
    host=os.getenv("MAIL_HOST", "smtp.qq.com"),
    port=int(os.getenv("MAIL_PORT", "465")),
    username=os.getenv("MAIL_USERNAME", ""),
    password=os.getenv("MAIL_PASSWORD", ""),
    use_tls=os.getenv("MAIL_USE_TLS", "false").lower() == "true",
    use_ssl=os.getenv("MAIL_USE_SSL", "true").lower() == "true",
    from_name=os.getenv("MAIL_FROM_NAME", "StockLLM"),
    from_address=os.getenv("MAIL_FROM_ADDRESS", ""),
)

DOUBAO_SETTINGS = ModelProviderSettings(
    base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
    model=os.getenv("ARK_MODEL", "doubao-seed-2-0-lite-260215"),
    api_key=os.getenv("ARK_API_KEY", ""),
)

OPENAI_SETTINGS = ModelProviderSettings(
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    api_key=os.getenv("OPENAI_API_KEY", ""),
)

QWEN_SETTINGS = ModelProviderSettings(
    base_url=os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    model=os.getenv("QWEN_MODEL", "qwen3.5-plus"),
    api_key=os.getenv("QWEN_API_KEY", ""),
)

XIAOMI_SETTINGS = ModelProviderSettings(
    base_url=os.getenv(
        "XIAOMI_BASE_URL",
        os.getenv("MIMO_BASE_URL", "https://token-plan-sgp.xiaomimimo.com/v1"),
    ),
    model=os.getenv("XIAOMI_MODEL", os.getenv("MIMO_MODEL", "mimo-v2.5-pro")),
    api_key=os.getenv("XIAOMI_API_KEY", os.getenv("MIMO_API_KEY", "")),
)

REPORT_LLM_PROVIDER = os.getenv("REPORT_LLM_PROVIDER", "xiaomi").strip().lower()
REPORT_ENABLE_WEB_SEARCH = os.getenv("REPORT_ENABLE_WEB_SEARCH", "").strip().lower()
