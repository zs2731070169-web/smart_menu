import asyncio
import logging
import os
import re
from dataclasses import dataclass
from typing import Any

import dotenv
from langchain_core.tools import ToolException

from agent import tool_registry, llm_client
from agent.messages import ConversationMessage
from agent.tools.base import ToolResult, ToolExecutionContext
from api import ApiMessageRequest
from config import config
from memory.manager import dialogue_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


@dataclass(frozen=True)
class ChatResponse:
    """ChatEngine.handle_chat 的统一返回结构

    success:   是否成功完成意图处理
    message:   自然语言回复（LLM 直答 / 错误提示 / 兜底语），为空表示走结构化数据
    data:      工具产出的结构化数据（如菜品列表、配送信息），为空表示纯文本回复
    """

    success: bool
    message: str | None = None
    data: Any = None


class ChatEngine:

    def __init__(self):
        # 工具注册器与 LLM 客户端在 agent/__init__.py 中初始化
        self.tool_registry = tool_registry
        self.client = llm_client
        # 最大返回token数
        self.max_tokens = 4096
        # 协调agent使用的llm
        self.agent_model = os.getenv("AGENT_MODEL")
        # 全局对话管理器，按 thread_id 隔离各用户的 Dialogues 状态
        self.dialogue_manager = dialogue_manager

    async def handle_chat(self, user_query: str, thread_id: str) -> ChatResponse:
        """
        执行意图识别，并调用工具，获得最终结果
        :return: ChatResponse 统一返回结构
        """
        logger.info(f"[handle_chat] 收到请求, thread_id: {thread_id}, user_query: {user_query}")

        invalid_query_list = ['""', '" "', "None", "null", "undefined", "nil"]

        if not user_query or not user_query.strip() or user_query.strip() in invalid_query_list:
            logger.warning(f"[handle_chat] 用户查询为空, thread_id: {thread_id}")
            return ChatResponse(success=False, message="抱歉，我没有收到您的查询，请您再试一次。")

        if not thread_id or not thread_id.strip():
            logger.warning(f"[chat] 会话ID为空")
            return ChatResponse(success=False, message="抱歉，会话ID无效，请您再试一次。。")

        # 每次请求注册该用户当前会话的对话状态
        self.dialogue_manager.register(thread_id)

        # 读取对话状态
        history = self.dialogue_manager.load_history(thread_id)
        logger.info(
            f"[chat] 历史记忆读取{'成功, 携带历史记录' if history else '完成, 无历史记录'}, thread_id: {thread_id}")

        # 构建消息列表
        user_query = f"历史对话记录: {history}\n用户查询: {user_query}\n" if history else f"用户查询: {user_query}\n"
        logger.info(f"[chat] 构建构建消息列表完成")

        try:
            # 根据用户输入获取自然语言查询
            try:
                llm_output = await self._calling_llm(user_query)
            except Exception as exc:
                if any(k in str(exc).lower() for k in ("connect", "timeout", "network")):
                    logger.error(f"[handle_chat] LLM 网络/超时, 进入关键词降级: {exc}")
                else:
                    logger.error(f"[handle_chat] LLM 异常, 进入关键词降级: {exc}", exc_info=True)
                # 降级处理用户查询，确保系统能够继续响应用户请求，而不是完全失败
                llm_output = _fallback(user_query)

            # llm 返回空或缺少必要字段
            if not llm_output or ('tool_name' not in llm_output and 'reply' not in llm_output):
                logger.error(f"[chat] 意图识别返回结果异常: {llm_output}")
                return ChatResponse(
                    success=False,
                    message="抱歉，处理您的查询时发生了错误，请稍后再试。"
                )

            # 没有 tool_name 表示 LLM 不再调用工具
            if 'tool_name' not in llm_output:
                reply = llm_output.get('reply') or "抱歉，我暂时没法回答这个问题。"
                # 返回结果前保存对话状态
                self.dialogue_manager.add_history(thread_id, query=user_query, content=reply)
                logger.info(f"[handle_chat] 主 LLM 直接回答, thread_id: {thread_id}")
                return ChatResponse(success=True, message=reply)

            tool_name = llm_output['tool_name']
            tool_input = llm_output.get('arguments', {})
            logger.info(f"[handle_chat] 路由至: {tool_name}, 参数: {tool_input}")

            # 调用工具
            tool_result = await self._tool_invoke(tool_name, tool_input)

            # 工具失败时返回错误信息
            if tool_result.is_error:
                logger.warning(f"[handle_chat] 工具 {tool_name} 执行失败: {tool_result.output}")
                return ChatResponse(
                    success=False,
                    message=tool_result.output or "抱歉，处理您的查询时发生了错误，请稍后再试。"
                )

            logger.info(
                f"[handle_chat] 请求处理完成, thread_id: {thread_id}, 结果类型: {type(tool_result.output).__name__}")
            return ChatResponse(
                success=True,
                data=tool_result.output
            )
        except Exception as e:
            logger.error(f"[handle_chat] 未预期错误, thread_id: {thread_id}, 错误: {e}", exc_info=True)
            return ChatResponse(
                success=False,
                message="抱歉，处理您的查询时发生了错误，请稍后再试。"
            )

    async def _calling_llm(self, user_query: str) -> dict[str, Any]:
        """
        执行llm返回工具调用或ai回复
        :return: 包含工具名称和处理后查询的字典
        """
        logger.info(f"[_calling_llm] 开始执行llm")
        # 调用大模型进行意图识别和工具选择
        response = await self.client.ainvoke_message(
            ApiMessageRequest(
                model=self.agent_model,
                message=ConversationMessage(role="user", content=[user_query]),
                system_prompt=config.INSTANTLY_PROMPT,
                max_tokens=self.max_tokens,
                tools=self.tool_registry.to_api_schema(),
            )
        )

        tool_calls = response.tool_calls
        # 不调用工具，模型直接给出回答
        if len(tool_calls) == 0:
            reply = response.content.strip() if response.content else ""
            if not reply:
                raise ValueError(f"未选择工具时必须提供回复内容: content 为空")
            logger.info(f"[_calling_llm] 直接回答, 长度: {len(reply)}")
            return {"reply": reply}
        # 需要使用工具时，取出工具名和工具参数
        else:
            tool_call = tool_calls[0]
            logger.info(f"[_calling_llm] 工具调用: {tool_call}")
            return tool_call

    async def _tool_invoke(self, tool_name: str, tool_input: dict[str, Any]) -> ToolResult:
        """
        根据用户问题和工具名称调用对应的工具，并返回工具执行结果
        :param tool_name: 需要调用的工具名称
        :param tool_input: 处理后的用户查询语句
        :return: 工具执行结果
        """
        logger.info(f"[_tool_invoke] 开始工具调用, tool_name: {tool_name}, query: {tool_input}")
        try:
            tool = self.tool_registry.get(tool_name)
            if tool is None:
                logger.warning(f"[_tool_invoke] 工具名称无效: {tool_name}")
                raise ToolException("抱歉，我无法处理您的查询，请您再试一次。")

            # 把 dict 转成模型实例，同时验证输入合法性
            parsed_input = tool.input_model.model_validate(tool_input)
            # 工具调用
            result = await tool.execute(
                parsed_input,
                ToolExecutionContext(
                    metadata={
                        "llm_client": self.client,
                        "max_tokens": self.max_tokens,
                    }
                )
            )
            logger.info(f"[_tool_invoke] 工具调用完成, tool_name: {tool_name}, is_error: {result.is_error}")
            return result
        except ToolException as te:
            logger.warning(f"[_tool_invoke] ToolException: {te}")
            return ToolResult(output=f"工具调用异常 {te}", is_error=True)
        except Exception as e:
            logger.error(f"[_tool_invoke] 工具调用异常, tool_name: {tool_name}, 错误: {e}", exc_info=True)
            return ToolResult(output=f"未知异常 {e}", is_error=True)


def _fallback(user_query: str) -> dict[str, Any]:
    """
    包装意图识别方法，增加手动降级处理
    降级方案: 列表关键词匹配、正则匹配、语义相似性匹配、LLM语义匹配、机器学习算法，这里使用列表关键词匹配
    :param user_query: 用户输入的自然语言查询
    :return: 包含工具名称和处理后查询的字典
    """
    logger.info(f"[_fallback] 开始关键词匹配降级, query: {user_query}")
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
        return {"tool_name": "delivery_check", "arguments": {"query": address}}
    elif any(keyword in user_query for keyword in menus):
        return {"tool_name": "menu_inquiry", "arguments": {"query": user_query}}
    else:
        return {
            "reply": "抱歉，我暂时没法理解您的问题，您可以问我菜品推荐或配送相关问题，也可以拨打 010-10293847 联系人工。"}


chat_engine = ChatEngine()


async def handle_chat(user_query: str, thread_id: str) -> ChatResponse:
    """
    进行智能客服对话
    :param user_query:
    :param thread_id:
    :return: 结构化数据
    """
    response = await chat_engine.handle_chat(user_query, thread_id)
    logger.info(f"[handle_chat] 对话完成, thread_id: {thread_id}, success: {response.success}")
    return response


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


    async def main():
        for query in test_queries:
            response = await handle_chat(query, test_thread_id)
            print(f"用户查询: {query}\n{response}\n")


    asyncio.run(main())
