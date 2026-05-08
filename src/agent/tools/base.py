from abc import ABC, abstractmethod
from dataclasses import field
from typing import Any

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class ToolResult:
    """标准工具返回对象"""

    output: str
    is_error: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """工具基类."""

    name: str
    description: str
    # type[BaseModel] 表示这是一个模型类本身，而非其实例。用于定义工具参数的 schema，可调用 model_json_schema() 生成 JSON schema
    input_model: type[BaseModel]

    @abstractmethod
    def execute(self, arguments: BaseModel) -> ToolResult:
        """执行工具"""

    def to_api_schema(self) -> dict[str, Any]:
        """序列化工具信息为 OpenAI function calling 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_model.model_json_schema(),
            },
        }


class ToolRegistry:
    """工具注册器."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """工具实例注册."""
        self._tools[tool.name] = tool

    def register_tools(self, tools: list[BaseTool]) -> None:
        """工具实例注册."""
        for tool in tools:
            self.register(tool)

    def get(self, name: str) -> BaseTool | None:
        """通过工具名获取工具实例."""
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        """返回工具实例列表."""
        return list(self._tools.values())

    def to_api_schema(self) -> list[dict[str, Any]]:
        """返回工具信息列表."""
        return [tool.to_api_schema() for tool in self._tools.values()]
