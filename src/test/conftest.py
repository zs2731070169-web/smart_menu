"""
回归测试公共配置。

由于项目以 `src/` 作为运行根目录（详见 run.py 的 `server.main:app` 与 systemd 配置），
此处把 `src/` 加入 sys.path，使 `import server.main` 等能在 pytest 下正确解析。
"""
import os
import sys
from pathlib import Path

import pytest

# 将 src 目录加入模块搜索路径
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# 测试期间使用稳定的占位环境变量，避免 dotenv 缺失或外部密钥读取失败
os.environ.setdefault("AGENT_MODEL", "test-agent-model")
os.environ.setdefault("DEFAULT_PATH_MODE", "riding")


@pytest.fixture
def app():
    """返回 FastAPI 应用实例。延迟导入，确保 sys.path 已注入。"""
    from server.main import app as fastapi_app
    return fastapi_app


@pytest.fixture
def client(app):
    """提供 TestClient，自动维护 cookie 以模拟会话。"""
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c
