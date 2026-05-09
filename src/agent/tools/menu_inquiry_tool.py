import asyncio
import json
import logging
import os

import dotenv
from pydantic import BaseModel, Field

from agent.messages import ConversationMessage
from agent.tools.base import BaseTool, ToolResult, ToolExecutionContext
from api import ApiMessageRequest
from config import config
from service.retrieval import search_menu_items_with_ids_scores

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


class MenuInquiryInput(BaseModel):
    """用户查询"""
    query: str = Field(description="用户查询")


class MenuInquiryTool(BaseTool):
    """处理菜单咨询：菜品推荐、菜品介绍、口味偏好等"""

    name = "menu_inquiry"
    description = "处理菜单咨询，例如：菜品推荐、菜品介绍、口味偏好等"
    input_model = MenuInquiryInput

    async def execute(self, arguments: MenuInquiryInput, context: ToolExecutionContext) -> ToolResult:
        try:
            query = arguments.query

            menus = await asyncio.to_thread(search_menu_items_with_ids_scores, query, 5)
            menu_contents = [menu for menu in menus["content"] if menu]
            query = f"检索到的相关菜品信息: {menu_contents}\n用户查询: {query}\n" \
                if menu_contents else f"暂无相关菜品信息\n用户查询: {query}\n"

            client = context.metadata.get("llm_client")
            llm_output = await client.ainvoke_message(
                ApiMessageRequest(
                    model=os.getenv("NLG_MODEL"),
                    message=ConversationMessage(role="user", content=[query]),
                    system_prompt=config.MENU_PROMPT,
                    max_tokens=context.metadata.get("max_tokens", 4096),
                )
            )

            if not llm_output:
                logger.warning(f"用户查询: {query}, 菜单咨询生成回复无有效JSON: {llm_output}")
                return ToolResult(output="抱歉，未能找到相关菜品信息，请您再试一次。", is_error=True)

            content = llm_output.content

            clean_output_json = json.loads(content)
            logger.info(f"用户查询: {query}, 菜单咨询提取有效JSON: {clean_output_json}")

            return ToolResult(output={
                "recommend_menus": clean_output_json.get("menus", []),
                "ids": clean_output_json.get("ids", []),
            })
        except Exception as e:
            logger.error(f"处理菜单咨询时发生错误: {e}")
            return ToolResult(output=f"抱歉，处理您的查询时发生了错误，{e}", is_error=True)


menu_inquiry_tool = MenuInquiryTool()
