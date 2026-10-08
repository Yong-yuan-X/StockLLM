import logging

from openai import OpenAI

from core.app_settings import OPENAI_SETTINGS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(funcName)s] [%(filename)s:%(lineno)d] [%(message)s]',
    datefmt='%Y-%m-%d %H:%M:%S'
)


DEFAULT_GPT_MODEL = OPENAI_SETTINGS.model
DEFAULT_OPENAI_BASE_URL = OPENAI_SETTINGS.base_url
DEFAULT_OPENAI_API_KEY = OPENAI_SETTINGS.api_key


def call_gpt_model(
    user_question,
    system_prompt="你是一名专业的A股股票分析助手，擅长整理数据、总结走势并生成清晰的投资分析报告。",
    model=DEFAULT_GPT_MODEL,
    temperature=0.2,
    max_tokens=2048,
    timeout=60,
):
    """调用 OpenAI GPT 模型，返回文本结果。"""
    api_key = DEFAULT_OPENAI_API_KEY
    if not api_key:
        logging.error("未配置 OPENAI_API_KEY 环境变量。")
        raise ValueError("请先配置 OPENAI_API_KEY，例如：export OPENAI_API_KEY='你的API Key'")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_question})

    try:
        logging.info("正在初始化 OpenAI 客户端，模型：%s，base_url：%s", model, DEFAULT_OPENAI_BASE_URL)
        client = OpenAI(
            api_key=api_key,
            base_url=DEFAULT_OPENAI_BASE_URL,
        )

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        logging.info("GPT 调用成功。")

        answer = response.choices[0].message.content
        return answer.strip() if answer else ""

    except Exception as e:
        logging.error("调用 GPT 失败：%s", str(e), exc_info=True)
        if "AuthenticationError" in str(e) or "401" in str(e):
            logging.error("=== 认证错误排查建议 ===")
            logging.error("1. 检查 OPENAI_API_KEY 是否正确")
            logging.error("2. 确认账号和项目具备所选模型的调用权限")
            logging.error("3. 确认 API Key 没有过期、撤销或受限")
        raise


if __name__ == "__main__":
    req_data = "请用一句话说明你可以如何帮助我生成股票分析报告。"
    try:
        result = call_gpt_model(req_data)
        logging.info("最终回答：%s", result)
    except Exception as e:
        logging.error("程序执行失败：%s", e)
