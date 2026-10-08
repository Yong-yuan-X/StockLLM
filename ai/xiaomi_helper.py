import logging

from openai import OpenAI

from core.app_settings import XIAOMI_SETTINGS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(funcName)s] [%(filename)s:%(lineno)d] [%(message)s]',
    datefmt='%Y-%m-%d %H:%M:%S'
)


XIAOMI_BASE_URL = XIAOMI_SETTINGS.base_url
XIAOMI_MODEL = XIAOMI_SETTINGS.model
XIAOMI_API_KEY = XIAOMI_SETTINGS.api_key

XIAOMI_WEB_SEARCH_TOOL = {
    "type": "web_search",
    "max_keyword": 3,
    "force_search": True,
    "limit": 1,
}


def _extract_usage(response):
    usage = getattr(response, "usage", None)
    if not usage:
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}

    def pick(obj, *keys):
        for key in keys:
            if isinstance(obj, dict) and key in obj:
                return obj.get(key)
            value = getattr(obj, key, None)
            if value is not None:
                return value
        return None

    input_tokens = pick(usage, "input_tokens", "prompt_tokens")
    output_tokens = pick(usage, "output_tokens", "completion_tokens")
    total_tokens = pick(usage, "total_tokens")
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def call_xiaomi_model_via_openai_sdk(
    user_question,
    system_prompt="你是一名专业的A股股票分析助手，擅长整理数据、总结走势并生成清晰的投资分析报告。",
    model=XIAOMI_MODEL,
    temperature=0.2,
    max_tokens=2048,
    timeout=60,
    enable_web_search=False,
    response_format=None,
    disable_thinking=False,
    return_metadata=False,
):
    """调用小米 MiMo OpenAI 兼容接口，默认不启用联网搜索。"""
    if not XIAOMI_API_KEY:
        logging.error("未配置 XIAOMI_API_KEY 或 MIMO_API_KEY 环境变量。")
        raise ValueError("请先配置 XIAOMI_API_KEY，例如：export XIAOMI_API_KEY='你的API Key'")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_question})

    try:
        logging.info("正在初始化 Xiaomi MiMo 兼容客户端，模型：%s，base_url：%s", model, XIAOMI_BASE_URL)
        client = OpenAI(
            base_url=XIAOMI_BASE_URL,
            api_key=XIAOMI_API_KEY,
        )

        request_kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout,
        }
        extra_body = {}
        if response_format:
            request_kwargs["response_format"] = response_format
        if disable_thinking:
            extra_body["thinking"] = {"type": "disabled"}
        if enable_web_search:
            request_kwargs["tools"] = [XIAOMI_WEB_SEARCH_TOOL]
            request_kwargs["tool_choice"] = "auto"
            extra_body["webSearchEnabled"] = True
        if extra_body:
            request_kwargs["extra_body"] = extra_body

        effective_web_search = enable_web_search
        web_search_error = None
        try:
            response = client.chat.completions.create(**request_kwargs)
        except Exception as e:
            raw_error = str(e)
            if enable_web_search and "webSearchEnabled is false" in raw_error:
                web_search_error = raw_error
                effective_web_search = False
                logging.warning("Xiaomi MiMo 联网搜索未启用或无权限，降级为普通对话：%s", raw_error)
                request_kwargs.pop("tools", None)
                request_kwargs.pop("tool_choice", None)
                fallback_extra_body = dict(request_kwargs.get("extra_body") or {})
                fallback_extra_body.pop("webSearchEnabled", None)
                if fallback_extra_body:
                    request_kwargs["extra_body"] = fallback_extra_body
                else:
                    request_kwargs.pop("extra_body", None)
                response = client.chat.completions.create(**request_kwargs)
            else:
                raise
        logging.info("Xiaomi MiMo 调用成功。")

        answer = response.choices[0].message.content
        answer = answer.strip() if answer else ""
        if return_metadata:
            return {
                "text": answer,
                "usage": _extract_usage(response),
                "model": getattr(response, "model", None) or model,
                "enable_web_search": effective_web_search,
                "response_summary": {
                    "response_type": type(response).__name__,
                    "choice_count": len(getattr(response, "choices", []) or []),
                    "finish_reason": getattr(response.choices[0], "finish_reason", None)
                    if getattr(response, "choices", None)
                    else None,
                    "content_length": len(answer),
                    "web_search_error": web_search_error,
                },
            }
        return answer

    except Exception as e:
        logging.error("调用 Xiaomi MiMo 失败：%s", str(e), exc_info=True)
        if "AuthenticationError" in str(e) or "401" in str(e):
            logging.error("=== 认证错误排查建议 ===")
            logging.error("1. 检查 XIAOMI_API_KEY 或 MIMO_API_KEY 是否正确")
            logging.error("2. 确认该 API Key 有所选模型的调用权限")
            logging.error("3. 确认 API Key 没有过期、撤销或受限")
        raise


if __name__ == "__main__":
    req_data = "请用一句话说明你可以如何帮助我生成股票分析报告。"
    try:
        result = call_xiaomi_model_via_openai_sdk(req_data)
        logging.info("最终回答：%s", result)
    except Exception as e:
        logging.error("程序执行失败：%s", e)
