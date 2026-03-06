import json
import os
import re
import time
from json import JSONDecodeError
from typing import Any

import dotenv
from langchain_core.tools import ToolException

from agent.agent_tools import general_inquiry_tool, menu_inquiry_tool, delivery_check_tool
from agent.memory import memory

from config import config

import logging

from tools.data_process_tool import extract_json_from_llm_output
from tools.llm_tool import llm_calling

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


class SmartAssistant:

    def __init__(self):
        # 初始化工具列表，包含基础咨询工具、菜单咨询工具和配送校验工具
        self.tool_names = ["general_inquiry", "menu_inquiry", "delivery_check"]
        # 设置最大重试次数，避免无限重试导致系统资源浪费
        self.max_retry = 5
        # 设置重试间隔因子，随着重试次数增加，间隔时间也会增加，避免过于频繁的重试
        self.interval_factor = 1.5

    def _identify_user_instantly_with_retry(self, user_query: str) -> dict[str, Any]:
        """
        包装意图识别方法，增加重试机制，在意图识别失败时进行重试
        :param user_query: 用户输入的自然语言查询
        :return: 包含工具名称和处理后查询的字典
        """
        logger.info(f"[_identify_user_instantly_with_retry] 开始意图识别, 最大重试次数: {self.max_retry}")
        error = ""
        for attempt in range(1, self.max_retry + 1):
            try:
                result = SmartAssistant._identify_user_instantly(user_query, error)

                logger.info(f"[_identify_user_instantly_with_retry] 第 {attempt} 次尝试成功, 结果: {result}")
                return result
            except (JSONDecodeError, ValueError) as e:
                # 达到最大重试次数，退出循环，进行降级处理
                if attempt == self.max_retry:
                    logger.error(f"[_identify_user_instantly_with_retry] 已达最大重试次数, 进入降级处理. 错误原因: {e}")
                    break

                sleep_time = self.interval_factor * attempt
                logger.warning(
                    f"[_identify_user_instantly_with_retry] 第 {attempt} 次失败, 原因: {e}, {sleep_time:.1f}s 后重试")
                error = str(e)

                # 随着重试次数增加，增加等待时间，避免过于频繁的重试
                time.sleep(sleep_time)

        # 最终降级处理用户查询，确保系统能够继续响应用户请求，而不是完全失败
        return SmartAssistant._identify_user_instantly_with_fallback(user_query)

    @staticmethod
    def _identify_user_instantly_with_fallback(user_query: str) -> dict[str, Any]:
        """
        包装意图识别方法，增加手动降级处理
        降级方案: 列表关键词匹配、正则匹配、语义相似性匹配、LLM语义匹配、机器学习算法，这里使用列表关键词匹配
        :param user_query: 用户输入的自然语言查询
        :return: 包含工具名称和处理后查询的字典
        """
        logger.info(f"[_identify_user_instantly_with_fallback] 开始关键词匹配降级, query: {user_query}")
        # 简单的列表匹配降级方案，根据用户查询中的关键词匹配工具
        delivers = ["配送", "送达", "外卖", "配送范围", "配送时间", "配送费用", "送餐时间", "外卖服务", "配送服务"]
        menus = ["推荐", "介绍", "口味", "菜品", "菜单", "菜式", "菜肴", "特色菜", "招牌菜", "新品"]

        if any(keyword in user_query for keyword in delivers):
            # 使用正则表达式提取地址信息，假设地址通常出现在关键词后面,
            address_match = re.search(r"(地址是|送到|送至)(?P<address>.+)", user_query)
            if address_match:
                address = address_match.group("address").strip()
            else:
                # 如果没有匹配到特定模式，可以将整个查询作为地址，或进行更复杂的处理
                address = user_query
            return {"tool_name": "delivery_check", "format_query": address}
        elif any(keyword in user_query for keyword in menus):
            return {"tool_name": "menu_inquiry", "format_query": user_query}
        else:
            return {"tool_name": "general_inquiry", "format_query": user_query}

    @staticmethod
    def _identify_user_instantly(user_query: str, error: str) -> dict[str, Any]:
        """
        根据用户输入的自然语言，分析并识别出最匹配的工具和处理后的查询语句
        :param error:
        :param user_query: 用户输入的自然语言查询
        :return: 包含工具名称和处理后查询的字典
        """
        logger.info(f"[_identify_user_instantly] 开始LLM意图识别, 携带上次错误: {'是' if error else '否'}")
        clean_output = None
        try:
            system_prompt = (config.INSTANTLY_PROMPT
                             + (f"\n\n前一次意图识别错误，原因: {error}\n请根据原因对错误进行纠正" if error else ""))

            # 调用大模型进行意图识别和工具选择
            llm_output = llm_calling(user_query, system_prompt)
            logger.info(f"[_identify_user_instantly] 大模型返回, 输出长度: {len(llm_output) if llm_output else 0}")

            # 提取有效json
            clean_output = extract_json_from_llm_output(llm_output)
            logger.info(
                f"[_identify_user_instantly] JSON提取{'成功' if clean_output else '失败'}, 内容: {clean_output}")

            # Bug3修复：clean_output 为 None 时提前抛出，避免 json.loads(None) 引发 TypeError
            if not clean_output:
                logger.error(f"[_identify_user_instantly] 未提取到有效JSON, 原始输出: {llm_output}")
                raise JSONDecodeError("意图识别未返回有效JSON内容", doc=llm_output or "", pos=0)

            # 解析大模型输出，提取工具名称和处理后的查询语句
            output = json.loads(clean_output)
            logger.info(f"[_identify_user_instantly] JSON解析成功: {output}")

            # Bug1修复：应为 key in output，检查字典是否包含必要字段
            if not all(key in output for key in ["tool_name", "format_query"]):
                logger.warning(f"[_identify_user_instantly] 缺少必要字段, 实际字段: {list(output.keys())}")
                raise ValueError(f"意图识别结果缺少必要字段: {output}，必须包含 'tool_name' 和 'format_query'")

            logger.info(
                f"[_identify_user_instantly] 识别成功, tool_name: {output['tool_name']}, format_query: {output['format_query']}")
            return output
        except JSONDecodeError as jde:
            logger.warning(f"[_identify_user_instantly] JSON序列化失败: {jde}")
            raise JSONDecodeError("Json字符串序列化失败", doc=clean_output or "", pos=jde.pos)
        except Exception as e:
            logger.error(f"[_identify_user_instantly] 意图识别异常: {e}", exc_info=True)
            raise e

    def _tool_invoke(self, tool_name: str, tool_query: str, history: list[dict]) -> str | dict[str, Any]:
        """
        根据用户问题和工具名称调用对应的工具，并返回工具执行结果
        :param history:
        :param tool_name: 需要调用的工具名称
        :param tool_query: 处理后的用户查询语句
        :return: 工具执行结果
        """
        logger.info(f"[_tool_invoke] 开始工具调用, tool_name: {tool_name}, query: {tool_query}")
        try:
            if tool_name not in self.tool_names:
                logger.warning(f"[_tool_invoke] 工具名称无效: {tool_name}, 可用工具: {self.tool_names}")
                raise ToolException("抱歉，我无法处理您的查询，请您再试一次。")

            tool_result = "工具调用失败，未找到对应工具。"
            if tool_name == "general_inquiry":
                tool_result = general_inquiry_tool.invoke({"query": tool_query, "history": history})
            elif tool_name == "menu_inquiry":
                tool_result = menu_inquiry_tool.invoke({"query": tool_query})
            elif tool_name == "delivery_check":
                tool_result = delivery_check_tool.invoke(
                    {"query": tool_query, "path_mode": os.getenv("DEFAULT_PATH_MODE")})

            logger.info(f"[_tool_invoke] 工具调用成功, tool_name: {tool_name}, 结果类型: {type(tool_result).__name__}")
            return tool_result
        except ToolException as te:
            logger.warning(f"[_tool_invoke] ToolException: {te}")
            raise ToolException("抱歉，我无法处理您的查询，请您再试一次。")
        except Exception as e:
            logger.error(f"[_tool_invoke] 工具调用异常, tool_name: {tool_name}, 错误: {e}", exc_info=True)
            raise Exception("抱歉，处理您的查询时发生了错误，请稍后再试。")

    def chat(self, user_query: str, thread_id: str) -> str:
        """
        执行意图识别，并调用工具，获得最终结果
        :return:
        """
        logger.info(f"[chat] 收到请求, thread_id: {thread_id}, user_query: {user_query}")

        invalid_query_list = ['""', '" "', "None", "null", "undefined", "nil"]

        if (not user_query or not user_query.strip()
                or any(user_query.strip() in invalid_query_list for invalid_query_list in invalid_query_list)):
            logger.warning(f"[chat] 用户查询为空, thread_id: {thread_id}")
            return "抱歉，我没有收到您的查询，请您再试一次。"

        if not thread_id or not thread_id.strip():
            logger.warning(f"[chat] 会话ID为空")
            return "抱歉，会话ID无效，请您再试一次。"

        try:
            # 读取内存记忆
            history = memory.recall(thread_id)
            logger.info(
                f"[chat] 历史记忆读取{'成功, 携带历史记录' if history else '完成, 无历史记录'}, thread_id: {thread_id}")

            # 构建大模型输入提示语
            prompt = f"历史对话记录: {history}\n用户查询: {user_query}\n" if history else f"用户查询: {user_query}\n"
            logger.info(f"[chat] 构建提示语完成")

            # 获取用户输入的自然语言查询
            llm_output = self._identify_user_instantly_with_retry(prompt)

            # 防御：确保意图识别结果包含必要字段
            if not llm_output or 'tool_name' not in llm_output or 'format_query' not in llm_output:
                logger.error(f"[chat] 意图识别返回结果异常: {llm_output}")
                return "抱歉，处理您的查询时发生了错误，请稍后再试。"

            logger.info(f"[chat] 意图识别完成, 路由至: {llm_output['tool_name']}")

            # 根据工具名称和处理后的查询语句调用对应的工具，并返回工具执行结果
            tool_result = self._tool_invoke(llm_output['tool_name'], llm_output['format_query'], history)

            # 回答结果写入记忆
            memory.add(thread_id, user_query, tool_result, "tool")
            logger.info(f"[chat] 对话记忆已写入, thread_id: {thread_id}")

            logger.info(f"[chat] 请求处理完成, thread_id: {thread_id}, 结果类型: {type(tool_result).__name__}")
            return tool_result
        except Exception as e:
            logger.error(f"[chat] 未预期错误, thread_id: {thread_id}, 错误: {e}", exc_info=True)
            return "抱歉，处理您的查询时发生了错误，请稍后再试。"


assistant = SmartAssistant()


def chat_assistant(user_query: str, thread_id: str):
    """
    进行智能客服对话
    :param user_query:
    :param thread_id:
    :return:
    """
    answer = assistant.chat(user_query, thread_id)
    logger.info(f"[chat_assistant] 对话完成, thread_id: {thread_id}, 回复: {answer}")
    if isinstance(answer, str):
        return {
            "message": answer
        }
    return answer


if __name__ == '__main__':
    """
    执行一系列重试测试和异常测试
    """
    test_thread_id = "test_thread_002"
    test_queries = [
        "有推荐的川菜吗？",  # 正常查询
        "",  # 空查询
        "外卖送到北京天安门要多久？",  # 正常查询
        "   ",  # 仅空格查询
        "你们的招牌菜是什么？",  # 正常查询
        None,  # None查询
        "我想知道外卖服务的配送范围是哪里。",  # 正常查询
        "有没有清淡一些的菜？",  # 正常查询
        "前面我问了什么问题？",  # 历史查询
        "外卖能送到我家吗？地址是上海市浦东新区世纪大道100号。",  # 正常查询
        "明天的天气如何？",  # 与工具无关的查询，测试降级处理

    ]

    for query in test_queries:
        response = chat_assistant(query, test_thread_id)
        print(f"用户查询: {query}\n{response}\n")
