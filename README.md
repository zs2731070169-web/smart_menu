# 智能点餐系统后端服务

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

智能点餐系统后端服务，基于 FastAPI 构建。通过 LLM 意图识别与工具调用、Pinecone 向量化菜品检索、高德地图配送范围校验，对外提供 REST 接口与多轮聊天会话能力。

## ✨ 核心功能

- **🤖 意图识别与工具调用**：基于大语言模型的智能路由，自动识别用户意图并调用相应工具
- **🔍 向量化菜品检索**：集成 Pinecone，实现高效的语义相似度菜品搜索
- **🚚 配送范围校验**：基于高德地图 API 的实时地理编码和路径规划
- **💬 多轮对话管理**：线程安全的会话历史管理，支持上下文关联
- **📊 MySQL 持久化**：菜品数据库管理和业务数据存储

## 🚀 快速开始

### 前置要求

- Python 3.8+
- MySQL 8.0+
- pip 包管理器

### 安装依赖

```bash
pip install -r requirements.txt
```

### 环境配置

复制 `.env.example` 为 `.env` 并填写相关配置：

```bash
cp .env.example .env
```

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `LLM_PROVIDER` | LLM 提供商 | `openai` |
| `API_KEY` | LLM API 密钥 | - |
| `API_BASE` | LLM 基座 URL | `https://dashscope.aliyuncs.com/compatible-mode/v1/` |
| `AGENT_MODEL` | 意图路由模型 | `qwen3.6-max-preview` |
| `NLG_MODEL` | 文案生成模型 | `qwen-max` |
| `EMBEDDING_MODEL` | 向量化模型 | `text-embedding-v4` |
| `AMAP_API_KEY` | 高德地图 API 密钥 | - |
| `MERCHANT_LONGITUDE` | 商户经度 | `116.310918` |
| `MERCHANT_LATITUDE` | 商户纬度 | `39.992873` |
| `DELIVERY_RADIUS` | 配送范围（米） | `3000` |
| `DEFAULT_PATH_MODE` | 路径模式 | `2`（骑行）|
| `PINECONE_API_KEY` | Pinecone API 密钥 | - |
| `PINECONE_ENV` | Pinecone 环境 | `us-east-1` |
| `PINECONE_INDEX_NAME` | Pinecone 索引名 | `smart-menu-index` |
| `MYSQL_HOST` | MySQL 主机 | `localhost` |
| `MYSQL_PORT` | MySQL 端口 | `3306` |
| `MYSQL_USER_NAME` | MySQL 用户名 | `root` |
| `MYSQL_USER_PASSWORD` | MySQL 密码 | - |
| `MYSQL_DB_NAME` | MySQL 数据库名 | `smart_menu` |

### 启动服务

**方式一：使用启动脚本**（推荐）
```bash
python run.py
```

**方式二：手动启动 Uvicorn**
```bash
cd src
uvicorn server.main:app --host 127.0.0.1 --port 8000
```

服务将在 `http://127.0.0.1:8000/smart/menu` 启动

## 📚 项目结构

```
src/
├── server/              # FastAPI 入口与路由层
│   ├── main.py         # 应用主体、中间件配置
│   ├── routes.py       # REST 接口定义
│   └── schemas/        # 请求/响应数据模型
├── service/            # 业务编排层
│   ├── menu.py         # 聊天处理、菜单同步
│   └── retrieval.py    # 向量检索逻辑
├── agent/              # 智能助手核心
│   ├── chat_engine.py  # 对话引擎（路由、工具调用）
│   ├── tools/          # 工具集
│   │   ├── base.py    # 工具基类与注册表
│   │   ├── menu_inquiry_tool.py     # 菜品查询工具
│   │   └── delivery_check_tool.py   # 配送校验工具
│   └── __init__.py    # 单例初始化
├── api/                # LLM 客户端抽象
│   ├── base_client.py  # 协议定义
│   ├── openai_client.py # OpenAI 兼容实现
│   └── __init__.py    # 工厂函数
├── clients/            # 第三方 SDK 封装
│   ├── amap_client.py        # 高德地图
│   ├── pinecone_client.py    # 向量数据库
│   ├── embedding_client.py   # 向量化服务
│   └── mysql_client.py       # MySQL 操作
├── repository/         # 数据访问层
│   └── menu_repo.py   # 菜品 DAO
├── memory/            # 会话管理
│   ├── manager.py     # 对话历史管理
│   └── types.py       # 数据类型定义
├── config/            # 配置与提示词
│   └── config.py      # 系统提示词、枚举映射
├── test/              # 单元测试
│   ├── conftest.py    # pytest 配置
│   └── test_*.py      # 测试用例
└── run.py             # 启动入口
```

## 🔗 API 接口

### 1. 菜单查询

```http
GET /smart/menu/query/menus?query=红烧肉
```

**响应示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "menus": [
      {
        "id": 1,
        "name": "红烧肉",
        "price": 28.0,
        "description": "精选猪五花，红烧入味"
      }
    ],
    "ids": [1]
  }
}
```

### 2. 配送范围检查

```http
GET /smart/menu/query/delivery?latitude=39.99&longitude=116.31
```

**响应示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "inDeliveryRange": true,
    "distance": 1250
  }
}
```

### 3. 多轮聊天

```http
POST /smart/menu/chat
Content-Type: application/json

{
  "query": "我想要一份红烧肉，请问能送到中关村吗？"
}
```

**响应示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "为您找到以下菜品...",
    "menus": [
      {
        "id": 1,
        "name": "红烧肉",
        "price": 28.0,
        "description": "精选猪五花，红烧入味"
      }
    ],
    "deliveryInfo": {
      "inRange": true,
      "distance": 1250
    }
  }
}
```

### 4. 开启新会话

```http
POST /smart/menu/new/chat
Content-Type: application/json

{
  "query": "你好"
}
```

## 🧪 测试

```bash
# 运行所有测试
cd src && pytest

# 运行特定测试文件
cd src && pytest test/test_chat_endpoint.py

# 运行单个测试用例
cd src && pytest test/test_chat_endpoint.py::test_chat_handles_query -v
```

## 🔧 菜单数据同步

### 从 MySQL 同步到 Pinecone

```bash
python -c "from service.menu import batch_sync_menu_index; batch_sync_menu_index()"
```

或在代码中调用：
```python
from service.menu import batch_sync_menu_index
batch_sync_menu_index()
```

## 📋 核心概念

### 对话流程

```
HTTP 请求
  ↓
SessionMiddleware（注入 session_id）
  ↓
service.menu.chat()
  ↓
agent.chat_engine.handle_chat()
  ↓
┌─ LLM 路由（AGENT_MODEL）
│  ├─ 识别意图
│  └─ 选择工具
│
└─ 工具执行
   ├─ MenuInquiryTool：菜品查询
   ├─ DeliveryCheckTool：配送校验
   └─ NLG 生成响应（NLG_MODEL）
```

### 工具系统

- **BaseTool**：所有工具的基类，支持自动 schema 生成
- **ToolRegistry**：全局工具注册表，管理工具的生命周期
- **ToolExecutionContext**：工具执行上下文，承载历史、参数等信息
- **ToolResult**：统一的工具执行结果格式

### 会话管理

- 基于 `thread_id`（从 session cookie 派生）隔离对话历史
- 线程安全的 `dialogue_manager` 单例
- 支持上下文关联的多轮对话

## 🔐 部署

### Systemd 服务

使用 `deploy/smart_menu.service` 以 systemd 进程管理：

```bash
sudo cp deploy/smart_menu.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start smart_menu
sudo systemctl status smart_menu
```

## 🛠️ 开发指南

### 添加新工具

1. 在 `agent/tools/` 下创建新工具文件，继承 `BaseTool`
2. 实现 `execute()` 方法
3. 在 `agent/__init__.py` 中注册工具
4. 在 `config/config.py` 中配置系统提示词

### 添加新 LLM Provider

1. 在 `api/` 下创建新的客户端实现，继承 `SupportsInvokeMessages`
2. 在 `api/__init__.py` 的 `_REGISTRY` 中注册
3. 更新 `.env.example` 中的 `LLM_PROVIDER`

### 修改系统行为

所有与意图识别、推荐策略、提示词相关的修改都应在 `config/config.py` 中进行。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📝 许可证

MIT License

## 📧 联系方式

- 项目地址：[GitHub](https://github.com/zs2731070169-web/smart_menu)
- 前端仓库：[smart_menu_ui](https://github.com/zs2731070169-web/smart_menu_ui)

---

**最后更新**：2026-05-09
