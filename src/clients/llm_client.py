# 大模型调用统一入口:所有 llm 调用都通过 api.SupportsStreamingMessages 协议转发
import logging
import os

import dotenv

from agent.messages import ConversationMessage
from api import ApiMessageRequest, ApiMessageResponse, get_llm_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


def llm_calling(
        query: str,
        system_prompt: str,
        model: str | None = None,
        provider: str | None = None,
        max_tokens: int = 4096,
) -> ApiMessageResponse:
    """
    统一的 llm 调用入口,返回结构化响应对象 ApiMessageResponse
    :param query: 用户输入
    :param system_prompt: 系统提示语
    :param model: 模型名称
    :param provider: llm provider 名称,缺省读取 LLM_PROVIDER 或使用 openai
    :param max_tokens: 生成最大 token 数
    """
    if not query or not system_prompt:
        raise ValueError("query 与 system_prompt 必填")

    if not model:
        raise ValueError("未指定模型")

    client = get_llm_client(provider)

    response = client.invoke_message(
        ApiMessageRequest(
            model=model,
            messages=[ConversationMessage(role="user", content=[query])],
            system_prompt=system_prompt,
            max_tokens=max_tokens,
        )
    )
    logger.info(
        f"[llm_calling] provider={provider or os.getenv('LLM_PROVIDER') or 'openai'} "
        f"model={response.model} finish_reason={response.finish_reason} "
        f"content_len={len(response.content)}"
    )
    return response


if __name__ == '__main__':
    print(
        llm_calling(
            query="请介绍一下智能菜单系统的功能和优势。",
            system_prompt="你是一个智能菜单系统的介绍者,负责向用户介绍智能菜单系统的功能和优势。",
            model=os.getenv('AGENT_MODEL')
        ).content
    )
