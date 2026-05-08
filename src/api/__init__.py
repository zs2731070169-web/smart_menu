"""llm 客户端工厂,支持按 provider 动态获取统一接口实现"""
import os
from typing import Callable

from api.base_client import ApiMessageRequest, ApiMessageResponse, SupportsInvokeMessages
from api.openai_client import OpenAIClient

# key为provider，value为有参数可调用客户端
_REGISTRY: dict[str, Callable[..., SupportsInvokeMessages]] = {
    "openai": OpenAIClient,
}

_cache: dict[str, SupportsInvokeMessages] = {}


def get_llm_client(provider: str | None = None) -> SupportsInvokeMessages:
    """按 provider 名称获取 llm 客户端;未指定时读取环境变量 LLM_PROVIDER,默认 openai"""
    key = (provider or os.getenv("PROVIDER") or "openai").lower()
    if key not in _REGISTRY:
        raise ValueError(f"未注册的 llm provider: {key}, 已注册: {list(_REGISTRY)}")
    if key not in _cache:
        # 根据provider动态创建客户端实例，并添加到缓存
        _cache[key] = _REGISTRY[key](api_key=os.getenv("API_KEY"), base_url=os.getenv("API_BASE"))
    return _cache[key]


__all__ = [
    "ApiMessageRequest",
    "ApiMessageResponse",
    "SupportsInvokeMessages",
    "get_llm_client"
]
