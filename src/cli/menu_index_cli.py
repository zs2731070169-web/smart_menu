import logging
import re
import uuid

import dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

from clients.embedding_client import embed_documents, embedding_model
from clients.pinecone_client import create_pinecone_index, clear_vectors, batch_insert
from service.menu import get_all_menus_for_index

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


def batch_sync_menu_index(batch_size: int = 30) -> bool:
    """
    初始化索引
    :return:
    """
    """
        批量同步菜单数据到Pinecone索引
        :param data:
        :param batch_size:
        :return:
        """
    try:
        # 1. 获取所有菜单项
        menus = get_all_menus_for_index()
        if not menus:
            return False

        # 2. 初始化Pinecone索引
        if not create_pinecone_index():
            return False

        # 3. 清除索引中的所有向量数据，确保每次同步都是全量更新
        if not clear_vectors():
            return False

        # 4. 把菜单文本进行切分
        split_menus = text_recursive_split(menus, chunk_size=100, chunk_overlap=20, separators=["\n"])
        if not split_menus:
            return False

        # 5. 使用向量模型把菜单文本转换为向量表示
        embeddings = embed_documents(split_menus)
        if not embeddings:
            return False

        # 6. 构建向量数据列表，每个元素包含向量表示和对应ID、元数据
        menu_vectors = []
        for line_num, (embedding, menu) in enumerate(zip(embeddings, split_menus), 1):
            # 判断维度是否匹配
            if len(embedding) != embedding_model.dimension:
                logger.error(f"Embedding dimension mismatch for menu: {menu}")
                continue

            menu_id = get_id(menu)  # 获取"每个菜品id: 5|"中的id作为菜单项的唯一标识
            meta_data = {
                "dish_id": menu_id,
                "content": menu,
                "line_number": line_num,
                "type": "menu_item",
            }
            vector_id = uuid.uuid4().hex  # 生成唯一的向量ID
            menu_vectors.append((vector_id, embedding, meta_data))

            if len(menu_vectors) >= batch_size:
                # 7. 把vector_data存储到pinecone向量数据库中
                batch_insert(menu_vectors)
                menu_vectors = []

        # 7. 存储剩余的向量数据
        if menu_vectors:
            batch_insert(menu_vectors)

        logger.info(f"Synced {len(split_menus)} menu chunks.")
    except Exception as e:
        print(f"Error during batch sync: {e}")
        return False

    return True


def text_recursive_split(text: str, chunk_size: int, chunk_overlap: int, separators: list[str]) -> list:
    """
    文本切分,使用langchain的递归切分
    :param separators:
    :param chunk_overlap:
    :param chunk_size:
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


def get_id(text: str) -> str:
    """
    从文本中提取id
    :param text:
    :return:
    """
    try:
        if not text.strip():
            logger.warning("Input text is empty or whitespace.")
            return ""

        # 使用正则提取获取"每个菜品id: 5|"里的id数值
        match = re.search(r"菜品id:\s*(\d+)", text)
        if match:
            # 获取第一个匹配组(\d+)里的数据
            return match.group(1)
        else:
            logger.warning("No ID found in the input text.")
            return ""
    except Exception as e:
        logger.error(f"Error extracting ID from text: {e}")
        return ""


if __name__ == '__main__':
    # menus = get_all_menus()
    # for menu in menus:
    #     print(menu)
    batch_sync_menu_index()
