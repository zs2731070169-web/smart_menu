import logging
import secrets
import uuid

from fastapi import FastAPI, Request, Query
from starlette.middleware.sessions import SessionMiddleware

from schemas.api_schemas import DeliveryReq, MenuResp, DeliveryResp, ChatResp
from service.menu_service import get_all_menus, check_delivery_endpoint, chat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Menu API",
    description="provides endpoints to access menu information for the smart ordering assistant",
    version="1.0.0",
    root_path="/smart/menu"
)

# 添加 SessionMiddleware 来处理基于签名的 cookie 会话
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_hex(32),
    max_age=3600,
    https_only=False,
    same_site="lax"
)


@app.get("/query/menus", response_model=MenuResp)
async def query_all_menus():
    """
    获取所有菜单项
    :return: 菜单项列表
    """
    logger.info(f"query_all_menus")
    return get_all_menus()


@app.post("/query/delivery", response_model=DeliveryResp)
async def query_delivery_endpoint(deliveryReq: DeliveryReq):
    """
    配送范围检查接口
    :return: 配送范围检查结果
    """
    logger.info(f"deliveryReq: {deliveryReq}")
    return check_delivery_endpoint(deliveryReq)


@app.get("/chat", response_model=ChatResp)
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
        response = chat(query, session_id)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResp(
            status=False,
            message={
                "message": "聊天服务发生错误，请稍后再试。"
            }
        )
    return response


@app.post("/new/chat")
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
