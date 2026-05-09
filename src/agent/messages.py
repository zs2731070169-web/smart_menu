from typing import Literal, Any

from openai import BaseModel
from pydantic import Field, field_validator


class ConversationMessage(BaseModel):
    """A single assistant or user message."""

    role: Literal["user", "assistant"]
    content: list[str] = Field(default_factory=list)

    @field_validator("content", mode="before")
    @classmethod
    def _normalize_content(cls, value: Any) -> list[Any]:
        """llm返回内容为空直接返回[]"""
        if value is None:
            return []
        return value
