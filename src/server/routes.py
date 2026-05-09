import logging
import uuid

from fastapi import APIRouter, Request, Query

from server.schemas.route_schemas import MenuResp, DeliveryResp, DeliveryReq, ChatResp
from service.menu import get_all_menus, check_delivery_endpoint, chat

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/query/menus", response_model=MenuResp)
async def query_all_menus():
    """
    获取所有菜单项
    :return: 菜单项列表
    """
    logger.info(f"query_all_menus")
    return get_all_menus()


@router.post("/query/delivery", response_model=DeliveryResp)
async def query_delivery_endpoint(deliveryReq: DeliveryReq):
    """
    配送范围检查接口
    :return: 配送范围检查结果
    """
    logger.info(f"deliveryReq: {deliveryReq}")
    return check_delivery_endpoint(deliveryReq)


@router.get("/chat", response_model=ChatResp)
async def chat_endpoint(
        request: Request,
        query: str = Query(default="", description="用户查询")
):
    """
    聊天接口，处理用户对话请求
    :param query: 用户输入的查询
    :param request: FastAPI Request 对象，用于访问会话
    :return:
    """
    try:
        logger.info(f"query: {query}, session_id: {request.session.get('session_id')}")
        session = request.session
        if "session_id" not in session:
            request.session["session_id"] = str(uuid.uuid4().hex)
        session_id = request.session.get("session_id")
        response = await chat(query, session_id)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResp(
            status=False,
            message="聊天服务发生错误，请稍后再试。"
        )
    return response


@router.post("/new/chat")
async def new_chat(request: Request) -> bool:
    """
    创建新的聊天会话，删除旧的session_id
    :return:
    """
    try:
        logger.info("New chat endpoint")
        session = request.session
        if "session_id" in session:
            request.session.pop("session_id", None)
    except Exception as e:
        logger.error(f"Error in new_chat endpoint: {e}")
        return False
    return True
