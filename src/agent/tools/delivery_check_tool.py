import asyncio
import logging
import os

import dotenv
from pydantic import BaseModel, Field

from agent.tools.base import BaseTool, ToolResult, ToolExecutionContext
from clients.amap_client import check_delivery_info, AMapConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


class DeliveryCheckInput(BaseModel):
    query: str = Field(description="用户提供的配送地址")


class DeliveryCheckTool(BaseTool):
    """处理配送范围检查：查询某个地址是否在配送范围内、能否送达等"""

    name = "delivery_check"
    description = "处理配送范围检查，例如：查询某个地址是否在配送范围内、能否送达等"
    input_model = DeliveryCheckInput

    async def execute(self, arguments: DeliveryCheckInput, context: ToolExecutionContext) -> ToolResult:
        try:
            query = arguments.query
            path_mode = os.getenv("DEFAULT_PATH_MODE")
            delivery_info = await asyncio.to_thread(check_delivery_info, query, path_mode)

            if not delivery_info.get("status", False):
                message = delivery_info.get("message", "")
                logger.warning(f"用户查询: {query}, 配送查询失败: {message}")
                if "RESULTS_ARE_EMPTY" in message:
                    out = "抱歉，无法规划到您提供地址的配送路线，请检查地址是否正确或是否超出配送范围。"
                elif "ENGINE_RESPONSE_DATA_ERROR" in message:
                    out = "抱歉，无法获取配送信息，请提供更详细的地址信息或稍后再试。"
                else:
                    out = message
                return ToolResult(output=out, is_error=True)

            logger.info(f"用户查询: {query}, 配送范围检查成功: {delivery_info}")

            distance = delivery_info.get('distance', '')
            duration = delivery_info.get('duration', '')
            formatted_address = delivery_info.get('formatted_address', '')

            out = (
                f"已查询到的配送信息:\n"
                f"- 格式化地址: {formatted_address or '未知'}\n"
                f"- 配送距离: {f'{distance}公里' if distance else '不可用'}\n"
                f"- 预计配送时间: {f'{duration}分钟' if duration else '不可用'}\n"
                f"- 是在最大配送范围内: {'可送达' if float(distance) <= AMapConfig.DELIVERY_RADIUS else '不可送达'}"
            )

            logger.info(f"用户查询: {query}, 配送查询生成回复: {out}")

            return ToolResult(output=out)
        except Exception as e:
            logger.error(f"处理配送范围检查时发生错误: {e}")
            return ToolResult(output="抱歉，处理您的查询时发生了错误，请稍后再试。", is_error=True)


delivery_check_tool = DeliveryCheckTool()
