from dataclasses import dataclass, field
from typing import Any, Protocol

from agent.messages import ConversationMessage


@dataclass(frozen=True)
class ApiMessageRequest:
    """统一的 llm 调用入参"""

    model: str
    messages: list[ConversationMessage]
    system_prompt: str | None = None
    max_tokens: int = 4096
    tools: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ApiMessageResponse:
    """统一的 llm 调用响应,屏蔽底层 sdk 差异"""

    content: str
    model: str
    finish_reason: str | None = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    raw: Any = None


class SupportsInvokeMessages(Protocol):
    """llm 客户端协议,所有 llm 调用统一通过该接口"""

    def invoke_message(self, request: ApiMessageRequest) -> ApiMessageResponse:
        """调用 llm 返回统一结构化响应"""
        ...
