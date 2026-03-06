import json
import logging
import os
from typing import Any

import dotenv
from langchain_core.tools import tool

from config import config
from tools.amap_tool import check_delivery_info
from tools.data_process_tool import extract_json_from_llm_output
from tools.llm_tool import llm_calling
from tools.retrieval_tool import search_menu_items_with_ids_scores

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


def general_inquiry(query: str, history: list[dict]) -> dict[str, Any]:
    """
    处理基础/常规咨询
    例如：营业时间、地址、联系方式、优惠活动等
    :param history:
    :param query:
    :return:
    """
    try:
        general_prompt = f"系统提示: {config.GENERAL_PROMPT}\n历史对话记录: {history}\n用户查询: {query}\n" \
            if history else f"系统提示: {config.GENERAL_PROMPT}\n用户查询: {query}\n"

        # 调用大模型生成回复
        content = llm_calling(query, general_prompt)

        logger.info(f"用户查询: {query}, 基础咨询生成回复: {content}")

        return {
            "message": content
        }
    except Exception as e:
        logger.error(f"处理基础咨询时发生错误: {e}")
        return "抱歉，处理您的查询时发生了错误，请稍后再试。"


def menu_inquiry(query: str) -> dict[str, Any] | str:
    """
    处理菜单咨询
    例如：菜品推荐、菜品介绍、口味偏好等
    :param query:
    :return:
    """
    try:
        menu_prompt = config.MENU_PROMPT

        # 检索菜品信息
        menus = search_menu_items_with_ids_scores(query, 5)

        # 过滤掉content为空的菜单项
        menu_contents = [menu for menu in menus["content"] if menu]
        # 构建大模型输入提示语
        prompt = f"检索到的相关菜品信息: {menu_contents}\n用户查询: {query}\n" \
            if menu_contents else f"暂无相关菜品信息\n用户查询: {query}\n"

        # 调用大模型生成回复,并使用大模型根据用户意图过滤检索结果
        llm_output = llm_calling(prompt, menu_prompt, model=os.getenv("CLOSEAI_RAG_MODEL"))

        # 提取有效json
        clean_output = extract_json_from_llm_output(llm_output)

        if not clean_output:
            logger.warning(f"用户查询: {query}, 菜单咨询生成回复无有效JSON: {llm_output}")
            return "抱歉，未能找到相关菜品信息，请您再试一次。"

        clean_output_json = json.loads(clean_output)

        logger.info(f"用户查询: {query}, 菜单咨询提取有效JSON: {clean_output_json}")

        return {
            "recommend_menus": clean_output_json.get("menus", []),
            "ids": clean_output_json.get("ids", []),
        }
    except Exception as e:
        logger.error(f"处理菜单咨询时发生错误: {e}")
        return "抱歉，处理您的查询时发生了错误，请稍后再试。"


def delivery_check(query: str, path_mode: str) -> dict[str, Any]:
    """
    处理配送范围检查
    例如：查询某个地址是否在配送范围内、能否送达等
    :param query:
    :param path_mode:
    :return:
    """
    try:
        delivery_info = check_delivery_info(query, mode=path_mode)

        if not delivery_info.get("status", False):
            message = delivery_info.get("message", "")
            logger.warning(f"用户查询: {query}, 配送查询失败: {message}")
            if "RESULTS_ARE_EMPTY" in message:
                return {"message": "抱歉，无法规划到您提供地址的配送路线，请检查地址是否正确或是否超出配送范围。"}
            elif "ENGINE_RESPONSE_DATA_ERROR" in message:
                return {"message": "抱歉，无法获取配送信息，请提供更详细的地址信息或稍后再试。"}
            return {"message": message}

        logger.info(f"用户查询: {query}, 配送范围检查成功: {delivery_info}")

        return {
            "formatted_address": f"配送地址：{delivery_info.get('formatted_address', '')}",
            "distance": f"配送距离：{delivery_info.get('distance', '')}公里" if delivery_info.get(
                "distance") else "配送距离信息不可用",
            "duration": f"配送时间：{delivery_info.get('duration', '')}分钟" if delivery_info.get(
                "duration") else "配送时间信息不可用"
        }
    except Exception as e:
        logger.error(f"处理配送范围检查时发生错误: {e}")
        return {"message": "抱歉，处理您的查询时发生了错误，请稍后再试。"}


general_inquiry_tool = tool(name_or_callable=general_inquiry)
menu_inquiry_tool = tool(name_or_callable=menu_inquiry)
delivery_check_tool = tool(name_or_callable=delivery_check)
