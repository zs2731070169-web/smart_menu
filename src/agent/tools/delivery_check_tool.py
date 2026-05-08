import logging
import os

import dotenv
from pydantic import BaseModel, Field

from agent.tools.base import BaseTool, ToolResult
from clients.amap_client import check_delivery_info

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

    def execute(self, arguments: DeliveryCheckInput) -> ToolResult:
        try:
            query = arguments.query
            path_mode = os.getenv("DEFAULT_PATH_MODE")
            delivery_info = check_delivery_info(query, mode=path_mode)

            if not delivery_info.get("status", False):
                message = delivery_info.get("message", "")
                logger.warning(f"用户查询: {query}, 配送查询失败: {message}")
                if "RESULTS_ARE_EMPTY" in message:
                    out = "抱歉，无法规划到您提供地址的配送路线，请检查地址是否正确或是否超出配送范围。"
                elif "ENGINE_RESPONSE_DATA_ERROR" in message:
                    out = "抱歉，无法获取配送信息，请提供更详细的地址信息或稍后再试。"
                else:
                    out = message
                return ToolResult(output=out, is_error=True, metadata={"message": out})

            logger.info(f"用户查询: {query}, 配送范围检查成功: {delivery_info}")
            metadata = {
                "formatted_address": f"配送地址：{delivery_info.get('formatted_address', '')}",
                "distance": f"配送距离：{delivery_info.get('distance', '')}公里" if delivery_info.get(
                    "distance") else "配送距离信息不可用",
                "duration": f"配送时间：{delivery_info.get('duration', '')}分钟" if delivery_info.get(
                    "duration") else "配送时间信息不可用",
            }
            return ToolResult(output=metadata["formatted_address"], metadata=metadata)
        except Exception as e:
            logger.error(f"处理配送范围检查时发生错误: {e}")
            return ToolResult(output="抱歉，处理您的查询时发生了错误，请稍后再试。", is_error=True)


delivery_check_tool = DeliveryCheckTool()
