import logging
import re
import uuid

import dotenv

from agent.smart_assistant import chat_assistant
from config.config import SPICE_LEVEL, IS_VEGETARIAN
from repository.menu_repo import get_all_menus_repo
from schemas.api_schemas import DeliveryReq, DeliveryResp, MenuResp, ChatResp
from tools.amap_tool import check_delivery_info
from tools.data_process_tool import text_recursive_split
from tools.embedding_tool import embed_documents, embedding_model
from tools.pinecone_tool import create_pinecone_index, clear_vectors, batch_insert

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


def chat(query: str, session_id: str) -> ChatResp:
    """
    处理用户的聊天查询
    :param query:
    :param session_id:
    :return:
    """
    response = chat_assistant(query, session_id)
    return ChatResp(
        status=True,
        message=response
    )


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
