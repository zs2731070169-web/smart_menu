# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介

智能点餐系统后端服务，基于 FastAPI 构建。核心能力：基于 LLM 的意图识别 + 工具调用、Pinecone 向量化菜品检索、高德地图配送范围校验，对外提供 REST 接口与多轮聊天会话。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器（uvicorn 监听 8000，从 src/run.py 入口启动）
python run.py

# 等价手动启动（必须在 src/ 下，因为模块路径以 src 为根）
cd src && uvicorn server.main:app --host 127.0.0.1 --port 8000

# 跑测试（pytest 位于 src/test，conftest.py 已把 src/ 注入 sys.path）
cd src && pytest
cd src && pytest test/test_chat_endpoint.py::test_chat_handles_query   # 单测
```

> 重要：项目以 `src/` 作为模块根，所有 import 都形如 `from agent.* import ...`、`from server.main import app`。在 IDE 或新脚本里运行时，需要把 `src/` 加入 `PYTHONPATH`，否则会 ImportError。systemd 单元（`deploy/smart_menu.service`）和测试 conftest 都遵循这一约定。

## 环境配置

复制 `.env.example` 为 `.env` 并填写：

| 变量 | 说明 |
|------|------|
| `PROVIDER` | LLM provider，目前仅 `openai`（OpenAI 兼容协议） |
| `API_KEY` / `API_BASE` | LLM 与 Embedding 共用的密钥/基座 URL |
| `AGENT_MODEL` | 路由/工具选择模型（`chat_engine._calling_llm` 使用） |
| `NLG_MODEL` | 工具内文案生成模型（菜单/配送工具使用） |
| `EMBEDDING_MODEL` | 向量化模型，如 `text-embedding-v4` |
| `DEFAULT_PATH_MODE` | 高德路径模式：`1`步行 / `2`骑行 / `3`驾车 |
| `AMAP_API_KEY` / `MERCHANT_LONGITUDE` / `MERCHANT_LATITUDE` / `DELIVERY_RADIUS` | 高德 + 商户配送起点配置 |
| `PINECONE_API_KEY` / `PINECONE_ENV` / `PINECONE_INDEX_NAME` | Pinecone Serverless |
| `MYSQL_HOST` / `MYSQL_PORT` / `MYSQL_USER_NAME` / `MYSQL_USER_PASSWORD` / `MYSQL_DB_NAME` | MySQL 连接 |

## 架构概览

### 目录与职责（src/ 下）

- `server/` — FastAPI 入口与路由层。`main.py` 装配 `SessionMiddleware`（签名 Cookie、3600s）和 `root_path=/smart/menu`；`routes.py` 暴露 `/query/menus`、`/query/delivery`、`/chat`、`/new/chat`；`schemas/route_schemas.py` 是请求/响应模型。
- `service/` — 业务编排层。`menu.py` 是 HTTP→Agent 的桥（`chat()`），并把 `ChatResponse.data` 按类型拆到 `ChatResp.data`/`message`；同时承担菜单全量同步到 Pinecone 的批处理（`batch_sync_menu_index`，可作为脚本独立运行）。`retrieval.py` 是向量召回。
- `agent/` — 智能助手核心。
  - `chat_engine.py` 是协调者：注入历史 → 路由 LLM 决策 → 单工具调用 → 失败时关键词降级（`_fallback`）。两次 LLM 调用：路由（`AGENT_MODEL` + `INSTANTLY_PROMPT` + tools schema）+ 工具内 NLG（`NLG_MODEL`）。**当前工具只支持单次调用、深度固定为 2**，没有 ReAct 多轮循环。
  - `tools/base.py` 定义 `BaseTool`、`ToolRegistry`、`ToolResult`、`ToolExecutionContext`；工具自动通过 `to_api_schema()` 暴露成 OpenAI function calling schema。
  - `tools/menu_inquiry_tool.py`、`tools/delivery_check_tool.py` 是仅有的两个业务工具（已不再有 `general_inquiry`，常规问候由路由 LLM 直接 `reply` 返回）。
  - `agent/__init__.py` 在导入时即构建 `tool_registry` 与 `llm_client` 单例。
- `api/` — LLM 客户端抽象层。`base_client.py` 是 `SupportsInvokeMessages` 协议；`openai_client.py` 是 OpenAI 兼容实现；`api/__init__.py` 的 `get_llm_client(provider)` 是工厂 + 单例缓存。新增 provider 在 `_REGISTRY` 注册即可。
- `clients/` — 第三方底层 SDK 封装：`amap_client.py`（地理编码 + 路径规划 + 距离判定）、`pinecone_client.py`、`embedding_client.py`、`mysql_client.py`（字典游标，支持 `with`）。
- `repository/` — DAO 层，目前只有 `menu_repo.py`，从 MySQL 读取菜品。
- `memory/` — 会话状态。`manager.py` 提供线程安全的 `dialogue_manager`，按 `thread_id` 隔离对话历史；`types.py` 是消息/对话数据类。
- `config/config.py` — 系统提示词集中地：`INSTANTLY_PROMPT`（路由）、`MENU_PROMPT`（菜品 NLG，强制 JSON `{menus, ids}`）、`DELIVERY_PROMPT`（配送 NLG），以及 `SPICE_LEVEL`、`IS_VEGETARIAN` 等枚举映射。**修改餐厅信息、推荐策略、意图识别规则一律改这里。**
- `test/` — pytest，`conftest.py` 注入 `src/` 到 `sys.path`、设占位 env、提供 `app` / `client` fixture（FastAPI TestClient，自动维持 cookie）。

### 请求链路

```
HTTP → server/routes.py
        ↓  (SessionMiddleware 注入 session_id)
       service/menu.chat(query, session_id)
        ↓
       agent/chat_engine.handle_chat
        ↓                                  历史在 memory/manager 里以 thread_id 索引
       _calling_llm  ── tool_calls 为空 ──→ 直答（仅返回 message）
        ↓ tool_call
       tool.execute (menu_inquiry | delivery_check)
        ↓                                  工具内部再调一次 NLG_MODEL
       ChatResponse(success, message, data) → ChatResp
```

### 前端契约（不可破坏）

- `menu_inquiry` 工具的 `output` 必须是 `{"recommend_menus": [...], "ids": [...]}` 结构化字典（来自 `MENU_PROMPT` 强制的 JSON），前端依赖 `ids` 数组渲染菜品卡片。
- `delivery_check` 工具的 `output` 是自然语言字符串，`service/menu.chat` 会落到 `ChatResp.message`。
- 路由 LLM 直答时 `data=None`，仅有 `message`。
- 改这两条任意一条都会让前端崩，需同步改 `service/menu.chat` 的拆包逻辑与对应 prompt。

### 降级与错误路径

- 路由 LLM 网络/超时失败 → `_fallback` 关键词匹配（含 `配送`/`推荐` 等词典），保证不全挂。
- 工具失败 → `ToolResult(is_error=True)`，`handle_chat` 把错误文案放进 `message`、`success=False`。
- 高德返回 `RESULTS_ARE_EMPTY` / `ENGINE_RESPONSE_DATA_ERROR` 在 `delivery_check_tool` 与 `service/menu.check_delivery_endpoint` 两处都做了用户友好文案翻译。

### 部署

- Nginx 反向代理 `/smart/menu/` → `127.0.0.1:8000`，前端静态文件外置（不在本仓库内）。
- Systemd `deploy/smart_menu.service`，`PYTHONPATH=/opt/smart_menu/src`。
- 域名 `www.ysccs.tech`，HTTPS，HTTP→HTTPS 强制重定向（见 `deploy/nginx.conf`）。

### 数据库

`sql/smart_menu.sql` 初始化脚本，含 `menu_items`、`users`、`orders`、`order_items`、`shopping_cart` 五张表。`service/menu.py::batch_sync_menu_index` 是把 `menu_items` 全量重建到 Pinecone 的入口（清空再写入），改菜品后需要跑一次。
