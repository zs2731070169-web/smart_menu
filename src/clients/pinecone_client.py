import logging
import os

import dotenv
from pinecone import Pinecone, ServerlessSpec

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


class PineconeTool:

    def __init__(self):
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY", "")
        self.pinecone_env = os.getenv("PINECONE_ENV", "us-east-1")

        self.pinecone = None
        self.index = None

        self.index_name = os.getenv("PINECONE_INDEX_NAME", "smart-menu-index")

        self.dimension = 1536

    def create_pinecone_index(self, index_name: str = None) -> bool:
        """
        初始化Pinecone连接并创建索引（如果不存在）
        :param index_name: 索引名称
        :return:
        """
        if not self.pinecone_api_key:
            logger.error("PINECONE_API_KEY is not set in environment variables.")
            return False
        if not self.pinecone_env:
            logger.error("PINECONE_ENV is not set in environment variables.")
            return False
        if not self.index_name:
            logger.error("PINECONE_INDEX_NAME is not set in environment variables.")
            return False

        index_name = index_name if index_name else self.index_name

        try:
            self.pinecone = Pinecone(api_key=self.pinecone_api_key)

            # 检查索引是否存在，如果不存在则创建
            if not self.pinecone.has_index(index_name):
                self.pinecone.create_index(
                    name=index_name,
                    vector_type="dense",
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.pinecone_env
                    )
                )
                logger.debug(f"Created index {index_name}")

            self.index = self.pinecone.Index(index_name)
            logger.info(f"Successfully initialized {index_name} index.")

            return True
        except Exception as e:
            logger.error(f"Failed to initialize {index_name} index: {e}")
            return False

    def clear_vectors(self, index_name: str = None) -> bool:
        """
        删除索引中的所有向量数据
        :return:
        """
        index_name = index_name if index_name else self.index_name

        # 在删除向量之前，先检查索引是否存在
        if not self.pinecone.has_index(index_name):
            logger.warning(f"{index_name} index does not exist")
            return True

        # 数据是否存在
        if self.index.describe_index_stats().total_vector_count == 0:
            logger.info(f"No vectors to clear in {index_name} index.")
            return True

        try:
            self.index.delete(delete_all=True)
            logger.info(f"Successfully cleared all vectors from {index_name} index.")
            return True
        except Exception as e:
            logger.error(f"Failed to clear vectors from {index_name} index: {e}")
            return False

    def search_similar(self, vector: list, top_k: int = 2, namespace: str = "__default__") -> list[str]:
        """
        相似性检索
        :param vector:
        :param top_k:
        :param namespace:
        :return:
        """
        try:
            if not self.index and not self.create_pinecone_index():
                logger.error("Pinecone index is not initialized.")
                return []

            results = self.index.query(
                namespace=namespace,
                vector=vector,
                top_k=top_k,
                include_metadata=True,
                include_values=False
            )

            logger.info(f"Found {len(results.matches)} similar vectors.")
        except Exception as e:
            logger.error(f"Failed to search for similar vectors: {e}")
            return []
        return results.matches

    def batch_insert(self, vector_data: list) -> bool:
        """
        批量插入向量数据到Pinecone索引
        :param vector_data: 包含向量表示和对应ID、元数据的列表
        :return:
        """
        try:
            if not vector_data:
                logger.warning("No vector data provided for insertion.")
                return False

            pinecone_tool.index.upsert(vectors=vector_data)
            logger.info(f"Successfully inserted {len(vector_data)} vectors into the index.")
            return True
        except Exception as e:
            logger.error(f"Failed to insert vectors into the index: {e}")
            raise


pinecone_tool = PineconeTool()


def clear_vectors(index_name: str = None) -> bool:
    """
    删除索引中的所有向量数据
    :return:
    """
    return pinecone_tool.clear_vectors(index_name=index_name)


def create_pinecone_index(index_name: str = None) -> bool:
    """
    初始化Pinecone连接并创建索引（如果不存在）
    :param index_name: 索引名称
    :return:
    """
    return pinecone_tool.create_pinecone_index(index_name=index_name)


def search_similar(vector: list, top_k: int = 2) -> list[str]:
    """
    相似性检索
    :param vector:
    :param top_k:
    :return:
    """
    return pinecone_tool.search_similar(vector=vector, top_k=top_k)


def batch_insert(vector_data: list) -> bool:
    """
    批量插入向量数据到Pinecone索引
    :param vector_data: 包含向量表示和对应ID、元数据的列表
    :return:
    """
    return pinecone_tool.batch_insert(vector_data=vector_data)


if __name__ == '__main__':
    pinecone_tool = PineconeTool()
    if pinecone_tool.create_pinecone_index():
        pinecone_tool.clear_vectors()
