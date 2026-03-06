import logging
import os
from typing import Union

import dashscope
import dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


class Embedding:
    def __init__(self):
        self.embedding_api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        self.embedding_model = os.environ.get("EMBEDDING_MODEL", "")
        self.dimension = 1536

    def embed(self, documents: Union[list | str]) -> list:
        try:
            if not documents:
                logger.warning("No documents provided for embedding.")
                return []

            # 单条字符串转为列表
            if isinstance(documents, str):
                documents = [documents]

            batch_size = 10
            all_embeddings = []
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                resp = dashscope.TextEmbedding.call(
                    model=self.embedding_model,
                    api_key=self.embedding_api_key,
                    input=batch,
                    dimension=self.dimension,
                )

                if resp.status_code != 200:
                    logger.error(f"Failed to get embedding: {resp.status_code} - {resp.message}")
                    return []

                if not resp.output['embeddings']:
                    logger.error(f"Invalid response format: {resp.data}")
                    return []

                logger.info(f"Embedding successfully generated for {len(documents)} documents.")
                all_embeddings.extend([embedding['embedding'] for embedding in resp.output['embeddings']])

            return all_embeddings
        except Exception as e:
            logger.error(f"Error calling Dashscope TextEmbedding API: {e}")
            return []


embedding_model = Embedding()


def embed_str(query: str) -> list:
    """
    全局向量化函数
    :param query:
    :return:
    """
    documents = embedding_model.embed(query)
    return documents[0] if documents else []


def embed_documents(documents: list[str]) -> list:
    """
    全局向量化
    :param documents:
    :return:
    """
    return embedding_model.embed(documents)


if __name__ == '__main__':
    embedding = Embedding()
    text = "这是一段测试文本，用于生成向量表示。"
    vector = embedding.embed([text])
    print(vector)
