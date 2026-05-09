import logging
import re

import dotenv

from agent.chat_engine import handle_chat
from clients.amap_client import check_delivery_info
from config.config import SPICE_LEVEL, IS_VEGETARIAN
from repository.menu_repo import get_all_menus_repo
from server.schemas.route_schemas import MenuResp, DeliveryReq, DeliveryResp, ChatResp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


def get_all_menus() -> MenuResp:
    """
    获取所有菜单项
    :return: 菜单项列表
    """
    try:
        menu_list = []
        for menu in get_all_menus_repo():
            menu_list.append(
                {
                    "id": menu.get("id"),
                    "dish_name": menu.get('dish_name'),
                    "price": menu.get('price'),
                    "description": menu.get("description").strip() if menu.get("description").strip() else "暂无描述",
                    "category": menu.get('category'),
                    "spice_level": SPICE_LEVEL.get(menu.get("spice_level")),
                    "flavor": menu.get("flavor").strip() if menu.get("flavor").strip() else "暂无口味信息",
                    "main_ingredients": menu.get("main_ingredients").strip() if menu.get(
                        "main_ingredients").strip() else "暂无主要食材信息",
                    "cooking_method": menu.get("cooking_method").strip() if menu.get(
                        "cooking_method").strip() else "暂无烹饪方法信息",
                    "is_vegetarian": IS_VEGETARIAN.get(menu.get("is_vegetarian")),
                    "allergens": menu.get("allergens").strip() if menu.get("allergens").strip() else "暂无过敏原信息",
                    "is_available": menu.get('is_available')
                }
            )

        logger.info("Successfully fetched all menus.")
        return MenuResp(
            menus=menu_list,
            status=bool(menu_list),
            message="Successfully query all menus." if menu_list else "No menus found.",
            count=len(menu_list)
        )
    except Exception as err:
        logger.error(f"Error fetching menus: {err}")
        return MenuResp(
            menus=[],
            status=False,
            message="查询菜品列表失败"
        )


def check_delivery_endpoint(deliveryReq: DeliveryReq) -> DeliveryResp:
    """
    获取配送地址的经纬度坐标
    :param address:
    :return:
    """
    try:
        delivery_info = check_delivery_info(deliveryReq.address, deliveryReq.mode)

        if not delivery_info['status']:
            logger.error(f"Failed to check delivery info for address: {deliveryReq.address}, mode: {deliveryReq.mode}")
            message = delivery_info.get("message", "")
            if "RESULTS_ARE_EMPTY" in message:
                message = "抱歉，无法规划到您提供地址的配送路线，请检查地址是否正确或是否超出配送范围。"
            elif "ENGINE_RESPONSE_DATA_ERROR" in message:
                message = "抱歉，无法获取配送信息，请提供更有效的地址信息。"
            return DeliveryResp(
                status=False,
                message=message
            )

        return DeliveryResp(
            status=True,
            in_range=delivery_info['in_range'],
            distance=delivery_info['distance'],
            duration=delivery_info['duration'],
            formatted_address=delivery_info['formatted_address']
        )
    except Exception as e:
        logger.error(f"Error in check_delivery_endpoint: {e}")
        return DeliveryResp(
            status=False,
            message=f"配送范围查询失败"
        )


async def chat(query: str, session_id: str) -> ChatResp:
    """
    处理用户的聊天查询
    :param query:
    :param session_id:
    :return:
    """
    response = await handle_chat(query, session_id)
    # 工具产出可能是结构化数据(dict, 如菜品推荐)或自然语言文本(str, 如配送回复),
    # 按类型分别落到 ChatResp 的 data / message 字段, 避免 Pydantic 校验失败
    data = response.data if isinstance(response.data, dict) else None
    message = response.message
    if message is None and isinstance(response.data, str):
        message = response.data
    return ChatResp(
        status=response.success,
        data=data,
        message=message,
    )


def get_all_menus_for_index():
    """
    获取所有菜单项
    :return: 菜单项列表
    """
    try:
        menu_list = []
        for menu in get_all_menus_repo():
            description = menu.get("description").strip() if menu.get("description").strip() else "暂无描述"
            allergens = menu.get("allergens").strip() if menu.get("allergens").strip() else "暂无过敏原信息"
            flavor = menu.get("flavor").strip() if menu.get("flavor").strip() else "暂无口味信息"
            main_ingredients = menu.get("main_ingredients").strip() if menu.get(
                "main_ingredients").strip() else "暂无主要食材信息"
            cooking_method = menu.get("cooking_method").strip() if menu.get(
                "cooking_method").strip() else "暂无烹饪方法信息"
            spice_level = SPICE_LEVEL.get(menu.get("spice_level"))
            is_vegetarian = IS_VEGETARIAN.get(menu.get("is_vegetarian"))

            menu_list.append(
                f"菜品id: {menu.get("id")}|菜品名称: {menu.get('dish_name')}|价格: {menu.get('price')}|描述: {description}|类别: {menu.get('category')}|辣度: {spice_level}|"
                f"口味: {flavor}|主要食材: {main_ingredients}|烹饪方法: {cooking_method}|是否素食: {is_vegetarian}|过敏原信息: {allergens}"
            )

        logger.info("Successfully fetched all menus.")
        return "\n".join(menu_list)
    except Exception as err:
        logger.error(f"Error fetching menus: {err}")
        return ""
