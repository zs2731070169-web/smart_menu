import json
import logging
import os

from openai import AsyncOpenAI

from api.base_client import ApiMessageRequest, ApiMessageResponse

logger = logging.getLogger(__name__)


class OpenAIClient:
    """openai 兼容协议(含 closeai)的 llm 客户端"""

    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: int = 120):
        if not api_key:
            raise ValueError("CLOSEAI_API_KEY 未配置")
        if not base_url:
            raise ValueError("CLOSEAI_API_BASE 未配置")
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    async def ainvoke_message(self, request: ApiMessageRequest) -> ApiMessageResponse:
        """使用 openai 接口调用,返回统一响应"""
        payload: list[dict] = []
        if request.system_prompt:
            payload.append({"role": "system", "content": request.system_prompt})
        payload.append({"role": request.message.role, "content": "\n".join(request.message.content)})

        kwargs: dict = {
            "model": request.model,
            "messages": payload,
            "max_tokens": request.max_tokens,
        }
        if request.tools:
            kwargs["tools"] = request.tools

        completion = await self._client.chat.completions.create(**kwargs)
        choice = completion.choices[0]

        # 解析 llm 返回的工具调用
        tool_calls: list[dict] = []
        for tool_call in (choice.message.tool_calls or []):
            try:
                # 反序列化工具参数为字典
                arguments = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                logger.warning(f"tool_call arguments JSON 解析失败: {tool_call.function.arguments}")
                arguments = {}

            # 创建工具调用字典对象，并添加到工具列表
            tool_calls.append({"tool_name": tool_call.function.name, "arguments": arguments})

        return ApiMessageResponse(
            content=choice.message.content or "",
            model=completion.model or request.model,
            finish_reason=choice.finish_reason,
            tool_calls=tool_calls,
            raw=completion,
        )
