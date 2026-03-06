# 大模型调用模板
import logging
import os
from dataclasses import dataclass

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


@dataclass
class LMTool:
    API_KEY = os.getenv("CLOSEAI_API_KEY", "")
    BASE_URL = os.getenv("CLOSEAI_API_BASE", "")
    MODEL = os.getenv("CLOSEAI_LLM_MODEL", "")

    if not API_KEY:
        raise ValueError("CLOSEAI_API_KEY environment variable is not set.")

    if not MODEL:
        raise ValueError("LLM_MODEL environment variable is not set.")

    if not BASE_URL:
        raise ValueError("DASHSCOPE_API_BASE environment variable is not set.")


def llm_calling(
        query: str,
        system_prompt: str,
        model: str = LMTool.MODEL):
    """
    调用大模型模板工具
    :param model:
    :param query: 用户输入的查询文本
    :param system_prompt: 系统提示语（可选）
    :param temperature: 生成文本的随机程度，值越高越随机（默认0.3）
    :param max_tokens: 生成文本的最大长度（默认2048）
    :return: 大模型生成的文本响应
    """
    if not query or not system_prompt:
        raise ValueError("Query or System_prompt must be provided.")

    prompt_template = ChatPromptTemplate([
        ("system", "{system_prompt}"),
        ("user", "{query}")
    ])

    llm = ChatOpenAI(
        model=model,
        api_key=LMTool.API_KEY,
        base_url=LMTool.BASE_URL,
        timeout=120
    )

    chain = prompt_template | llm

    llm_output = chain.invoke({
        "system_prompt": system_prompt,
        "query": query
    })

    logger.info("LLM response generated successfully.")

    return llm_output.content


if __name__ == '__main__':
    print(
        llm_calling(
            query="请介绍一下智能菜单系统的功能和优势。",
            system_prompt="你是一个智能菜单系统的介绍者，负责向用户介绍智能菜单系统的功能和优势。"
        )
    )
