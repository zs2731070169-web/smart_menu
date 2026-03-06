import logging
from typing import Any

from tools.embedding_tool import embed_str, embedding_model
from tools.pinecone_tool import search_similar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_menu_items(query: str, top_k: int = 2) -> list[str]:
    """
    返回仅有content的列表
    :param query:
    :param top_k:
    :return:
    """
    match_items = search_similar_menu_items(query, top_k)
    return [match_items['content'] for match_items in match_items if match_items['content']]


def search_menu_items_with_ids_scores(query: str, top_k: int = 2) -> dict[str, Any]:
    """
    返回带id和score的列表
    :param query:
    :param top_k:
    :return:
    """
    match_items = search_similar_menu_items(query, top_k)

    if not match_items:
        logger.warning(f"用户查询: {query}, 没有检索到对应结果: {match_items}")
        return {"content": [], "scores": [], "ids": []}

    contents, scores, ids = zip(*[
        (
            match_items['content'],
            match_items["score"],
            match_items["id"]
        )
        for match_items in match_items if match_items
    ])

    return {
        "content": contents,
        "scores": scores,
        "ids": ids
    }


def search_similar_menu_items(query: str, top_k: int = 2) -> list[str]:
    """
    根据用户问题进行相似性检索
    :param query:
    :param top_k:
    :return:
    """
    if not query:
        logger.warning(f"用户问题无效：{query}")
        return []

    # 嵌入为向量
    embedding = embed_str(query)

    if not embedding:
        logger.error(f"查询: {query}, 嵌入向量失败: {embedding}")
        return []

    # 向量维度校验
    if embedding_model.dimension != len(embedding):
        logger.error(f"Embedding dimension mismatch for query: {query}")
        return []

    # 相似性检索
    results = search_similar(embedding, top_k)

    if not results:
        logger.warning(f"用户查询: {query}, 没有检索到对应结果: {results}")
        return []

    match_items = []
    for result in results:
        match_items.append(
            {
                "id": result["id"],
                "score": result["score"],
                "content": result["metadata"]["content"],
                "line_number": result["metadata"]["line_number"],
            }
        )

    logger.info(f"成功查询到最终有效结果" if match_items else "无法查询到有效结果")

    return match_items


if __name__ == '__main__':
    print(search_similar_menu_items("给我推荐几道川菜"))
    print(search_menu_items_with_ids_scores("给我推荐几道川菜"))
    print(search_menu_items("给我推荐几道川菜"))
