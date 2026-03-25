# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介

智能点餐系统后端服务，基于 FastAPI + LangChain + Pinecone 构建，集成大模型意图识别、向量化菜品检索、高德地图配送范围验证，提供智能客服聊天能力。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器（监听 8000 端口）
python run.py

# 生产环境（systemd）
systemctl start smart_menu
systemctl status smart_menu

# 手动生产启动
cd src && uvicorn api.main:app --host 127.0.0.1 --port 8000
```

## 环境配置

复制 `.env.example` 为 `.env` 并填写以下密钥：

| 变量 | 说明 |
|------|------|
| `AMAP_API_KEY` | 高德地图 API 密钥 |
| `MERCHANT_LONGITUDE/LATITUDE` | 商户经纬度（配送起点） |
| `DELIVERY_RADIUS` | 配送半径（米），默认 3000 |
| `DASHSCOPE_API_KEY` | 阿里云 DashScope（向量化） |
| `CLOSEAI_API_KEY` | CloseAI（OpenAI 兼容，用于 LLM） |
| `PINECONE_API_KEY` | Pinecone 向量数据库 |
| `MYSQL_*` | MySQL 连接配置 |

## 架构概览

### 请求链路

```
HTTP请求 → FastAPI (api/main.py)
             ↓
        业务服务层 (service/menu_service.py)
             ↓
        智能助手 (agent/smart_assistant.py)
             ↓
        意图识别 (LLM → 3个工具之一)
             ↓
    ┌────────┬─────────────┬──────────────┐
    │ 基础咨询 │   菜品推荐   │   配送检查    │
    │  LLM   │ Pinecone+LLM│  高德地图API  │
    └────────┴─────────────┴──────────────┘
```

### 核心模块说明

**`src/agent/smart_assistant.py`** — 智能助手核心，负责意图识别。
- 优先调用 LLM（CloseAI）解析用户意图，提取 `tool_name` 和 `format_query`
- 失败时降级为关键词匹配（5次重试，指数退避）
- 三种意图：`general_inquiry`、`menu_inquiry`、`delivery_check`

**`src/agent/agent_tools.py`** — 三个工具的实现：
- `general_inquiry_tool`：直接调用 LLM，使用 `GENERAL_PROMPT` 系统提示词回复营业时间/地址等常规问题
- `menu_inquiry_tool`：向量化用户查询 → Pinecone 相似检索 Top-5 菜品 → LLM 生成推荐，返回 JSON（含菜品 ID 列表）
- `delivery_check_tool`：高德地图地址编码 → 路线规划 → 距离/时间计算

**`src/agent/memory.py`** — 线程安全的内存会话存储，以 `thread_id`（session_id）为 key。

**`src/config/config.py`** — 系统提示词（`GENERAL_PROMPT`、`MENU_PROMPT`、`INSTANTLY_PROMPT`）集中管理，修改餐厅信息、菜品推荐策略、意图识别规则都在此文件。

**`src/tools/`** — 底层工具封装：
- `llm_tool.py`：CloseAI LangChain ChatOpenAI 封装，两个模型：`CLOSEAI_LLM_MODEL`（对话）、`CLOSEAI_RAG_MODEL`（RAG/检索）
- `embedding_tool.py`：DashScope `text-embedding-v4`，1536 维，批处理 10 条/批
- `pinecone_tool.py`：Pinecone Serverless (AWS us-east-1)，余弦相似度
- `amap_tool.py`：高德 Geocode + Direction API，支持步行/骑行/驾车
- `db_tool.py`：MySQL 连接，字典游标，支持 `with` 上下文管理器

### API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/query/menus` | GET | 获取全部菜单 |
| `/query/delivery` | POST | 配送范围检查（传 `address`、`mode`） |
| `/chat` | GET | 智能客服聊天（传 `query`，基于 session Cookie） |
| `/new/chat` | POST | 重置聊天会话 |

会话通过签名 Cookie（`session_id`）维护，超时 3600 秒。

### 数据库

`sql/smart_menu.sql` 初始化脚本，5张表：`menu_items`（25 道菜）、`users`、`orders`、`order_items`、`shopping_cart`。

### 部署

- Nginx 反向代理：`/smart/menu/` → `http://127.0.0.1:8000`，前端静态文件 `/opt/smart_menu/ui/dist`
- Systemd 服务：`deploy/smart_menu.service`，`PYTHONPATH` 指向 `/opt/smart_menu/src`
- SSL 域名：`www.ysccs.tech`