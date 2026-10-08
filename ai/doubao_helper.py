import logging
from pprint import pformat

from openai import OpenAI

from core.app_settings import DOUBAO_SETTINGS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(funcName)s] [%(filename)s:%(lineno)d] [%(message)s]',
    datefmt='%Y-%m-%d %H:%M:%S'
)


ARK_BASE_URL = DOUBAO_SETTINGS.base_url
ARK_MODEL = DOUBAO_SETTINGS.model
ARK_API_KEY = DOUBAO_SETTINGS.api_key


def _extract_response_text(response):
    """兼容 Responses API 的常见输出结构，提取最终文本。"""
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text.strip()

    output = getattr(response, "output", None) or []
    text_parts = []
    for item in output:
        contents = getattr(item, "content", None) or []
        for content in contents:
            content_type = getattr(content, "type", "")
            if content_type == "output_text":
                text_value = getattr(content, "text", "")
                if text_value:
                    text_parts.append(str(text_value))
                annotations = getattr(content, "annotations", None) or []
                for annotation in annotations:
                    annotation_text = getattr(annotation, "text", None)
                    if annotation_text:
                        text_parts.append(str(annotation_text))
            elif content_type in {"text", "summary_text"}:
                text_value = getattr(content, "text", "") or getattr(content, "value", "")
                if text_value:
                    text_parts.append(str(text_value))
            else:
                for attr_name in ("text", "value", "output_text"):
                    attr_value = getattr(content, attr_name, None)
                    if attr_value:
                        text_parts.append(str(attr_value))

    return "\n".join(text_parts).strip()


def _truncate_text(value, max_length=800):
    text = str(value or "").strip()
    if len(text) <= max_length:
        return text
    return f"{text[:max_length]}..."


def _safe_model_dump(response):
    model_dump = getattr(response, "model_dump", None)
    if callable(model_dump):
        try:
            return model_dump()
        except Exception:
            return None
    return None


def _summarize_response(response):
    output = getattr(response, "output", None) or []
    output_items = []
    for item in output[:8]:
        item_summary = {
            "type": getattr(item, "type", None),
            "role": getattr(item, "role", None),
        }
        contents = getattr(item, "content", None) or []
        content_summaries = []
        for content in contents[:10]:
            content_summaries.append(
                {
                    "type": getattr(content, "type", None),
                    "text_preview": _truncate_text(
                        getattr(content, "text", None)
                        or getattr(content, "value", None)
                        or getattr(content, "output_text", None)
                    ),
                }
            )
        if content_summaries:
            item_summary["content"] = content_summaries
        output_items.append(item_summary)

    dumped = _safe_model_dump(response)
    raw_preview = None
    if dumped is not None:
        raw_preview = _truncate_text(pformat(dumped, width=100), max_length=2400)

    return {
        "response_type": type(response).__name__,
        "has_output_text": bool(getattr(response, "output_text", None)),
        "output_length": len(output),
        "incomplete_reason": getattr(getattr(response, "incomplete_details", None), "reason", None)
        if getattr(response, "incomplete_details", None) is not None
        else (getattr(response, "incomplete_details", None) or {}).get("reason")
        if isinstance(getattr(response, "incomplete_details", None), dict)
        else None,
        "output_items": output_items,
        "raw_preview": raw_preview,
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


def call_ark_model_via_openai_sdk(
    user_question,
    system_prompt="你是一名专业的A股股票分析助手。请优先使用联网搜索获取最新公开信息，再给出简明、可靠的回答。",
    model=ARK_MODEL,
    enable_web_search=True,
    max_output_tokens=2048,
    timeout=60,
    return_metadata=False,
):
    """调用火山方舟模型；默认启用联网搜索。"""
    if not ARK_API_KEY:
        logging.error("未配置 ARK_API_KEY 环境变量。")
        raise ValueError("请先配置 ARK_API_KEY，例如：export ARK_API_KEY='你的API Key'")

    input_items = []
    if system_prompt:
        input_items.append({"role": "system", "content": system_prompt})
    input_items.append({"role": "user", "content": user_question})

    request_kwargs = {
        "model": model,
        "input": input_items,
        "max_output_tokens": max_output_tokens,
        "timeout": timeout,
    }
    if enable_web_search:
        request_kwargs["tools"] = [{"type": "web_search"}]

    try:
        logging.info(
            "正在初始化 Doubao 兼容客户端，模型：%s，联网搜索：%s",
            model,
            enable_web_search,
        )
        client = OpenAI(
            base_url=ARK_BASE_URL,
            api_key=ARK_API_KEY,
        )

        response = client.responses.create(**request_kwargs)
        answer = _extract_response_text(response)
        response_summary = _summarize_response(response)
        if not answer:
            error = ValueError("模型返回成功，但未解析到文本内容。")
            setattr(error, "response_summary", response_summary)
            raise error

        if return_metadata:
            return {
                "text": answer,
                "usage": _extract_usage(response),
                "model": model,
                "enable_web_search": enable_web_search,
                "response_summary": response_summary,
            }
        return answer

    except Exception as e:
        logging.error("调用失败：%s", str(e), exc_info=True)
        if "AuthenticationError" in str(e) or "401" in str(e):
            logging.error("=== 认证错误排查建议 ===")
            logging.error("1. 检查 ARK_API_KEY 是否是火山方舟控制台生成的正确 API Key")
            logging.error("2. 确认该 API Key 有对应模型和工具能力的调用权限")
            logging.error("3. 确保 API Key 没有过期或被禁用")
        raise


if __name__ == "__main__":
    req_data = "现在的上证指数是多少？"
    try:
        result = call_ark_model_via_openai_sdk(req_data)
        logging.info("最终回答：%s", result)
    except Exception as e:
        logging.error("程序执行失败：%s", e)
