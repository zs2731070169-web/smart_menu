import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def text_recursive_split(text: str, chunk_size: int, chunk_overlap: int, separators: list[str]) -> list:
    """
    文本切分,使用langchain的递归切分
    :param text:
    :return:
    """
    try:
        if not text.strip():
            logger.warning("Input text is empty or whitespace.")
            return []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            keep_separator=False,
            add_start_index=False,
            length_function=len
        )
        split_list = text_splitter.split_text(text.strip())

        if not split_list:
            logger.warning("No chunks created from the input text.")
            return []

        logger.info("chunks created")
        return split_list
    except Exception as e:
        logger.error(f"Error during text splitting: {e}")
        return []


def extract_json_from_llm_output(llm_output: str) -> str:
    """
        从大模型输出中提取有效的JSON字符串，清洗掉多余的格式和字符
        处理大模型输出可能包含的```json```标记和其他非JSON内容，确保返回一个干净的JSON字符串以供后续解析使用
        例如，大模型输出可能是：
        ```
        ```json
        {
            "tool_name": "general_inquiry",
            "format_query": "请告诉我今天的特价菜有哪些？"
        }
        ```
        ```
        需要提取出其中的JSON部分：
        ```
        {
            "tool_name": "general_inquiry",
            "format_query": "请告诉我今天的特价菜有哪些？"
        }
        ```
    :param self:
    :param llm_output:
    :return:
    """
    try:
        clean_output = llm_output

        # 如果输出包含```json```标记，去掉这些标记
        if llm_output.startswith("```json") and llm_output.endswith("```"):
            clean_output = llm_output[7:-3].strip()

        # 获取有效的JSON字符串，避免任何额外字符干扰解析
        start = clean_output.find("{")
        end = clean_output.rfind("}")
        clean_output = llm_output[start: end + 1].strip()

        logger.info(f"{clean_output}")

        return clean_output
    except Exception as e:
        logger.error(f"Error extracting JSON from LLM output: {e}")
        return ""
