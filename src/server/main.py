import logging
import secrets

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from server.routes import router

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

# 注册路由
app.include_router(router)
