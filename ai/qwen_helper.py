from openai import OpenAI

from core.app_settings import QWEN_SETTINGS

QWEN_BASE_URL = QWEN_SETTINGS.base_url
QWEN_MODEL = QWEN_SETTINGS.model
QWEN_API_KEY = QWEN_SETTINGS.api_key


def build_qwen_client():
    if not QWEN_API_KEY:
        raise ValueError("请先配置 QWEN_API_KEY")
    return OpenAI(base_url=QWEN_BASE_URL, api_key=QWEN_API_KEY)
