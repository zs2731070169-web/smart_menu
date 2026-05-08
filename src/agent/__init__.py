"""agent 包初始化：在导入时构建工具注册器与 LLM 客户端单例"""
import logging
import os

import dotenv

from agent.tools.base import ToolRegistry
from agent.tools.delivery_check_tool import delivery_check_tool
from agent.tools.menu_inquiry_tool import menu_inquiry_tool
from api import get_llm_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


def _init_tools() -> ToolRegistry:
    """初始化工具注册器，统一注册基础咨询、菜单咨询、配送校验工具"""
    registry = ToolRegistry()
    registry.register_tools([menu_inquiry_tool, delivery_check_tool])
    logger.info("工具初始化完成")
    return registry


def _init_llm():
    """初始化 LLM 客户端"""
    llm_client = get_llm_client(os.getenv("PROVIDER"))
    logger.info("LLM 客户端初始化完成")
    return llm_client


tool_registry: ToolRegistry = _init_tools()
llm_client = _init_llm()

__all__ = ["tool_registry", "llm_client"]
