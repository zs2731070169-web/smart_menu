# Repository Guidelines

## 项目结构与模块组织
- `src/` 为后端代码目录。
- `src/api/` 定义 FastAPI 入口与接口路由。
- `src/service/`、`src/repository/`、`src/tools/`、`src/agent/` 分别承载业务逻辑、数据访问、工具集成与助手编排。
- `src/schemas/` 存放请求/响应与领域模型。
- `ui/` 为 Vue 3 + Vite 前端（核心在 `ui/src/components`、`ui/src/api`、`ui/src/App.vue`）。
- `sql/` 存放数据库脚本（如 `sql/smart_menu.sql`）。
- `deploy/` 存放部署配置（如 `nginx.conf`、`smart_menu.service`）。

## 构建、测试与开发命令
- 后端安装依赖：`pip install -r requirements.txt`
- 启动后端开发服务：`python run.py`（Uvicorn 默认端口 `8000`）
- 前端安装依赖：`cd ui && npm install`
- 前端开发运行：`npm run dev`
- 前端生产构建：`npm run build`
- 前端构建预览：`npm run preview`

## 编码风格与命名规范
- Python 使用 4 空格缩进；函数/变量用 `snake_case`，类名用 `PascalCase`。
- Vue/JS 在 SFC 中保持 2 空格缩进；函数/变量用 `camelCase`，组件文件用 `PascalCase`（如 `ChatAssistant.vue`）。
- 按分层组织代码：`api -> service -> repository`，避免跨层直接调用。
- 错误处理应明确、可追踪，接口报错信息要可读。

## 测试规范
- 当前仓库未内置完整自动化测试。
- 后端新增复杂逻辑时，建议在 `tests/` 下补充 `pytest` 用例。
- 前端改动至少执行 `npm run build`，并验证移动端与桌面端关键流程。
- 测试命名建议表达行为，例如：`test_delivery_out_of_range_returns_false`。

## 提交与合并请求规范
- 历史提交以“简短、任务导向”为主（多为中文），如：`优化 ChatAssistant.vue 组件样式...`。
- 推荐提交格式：`<type>: <scope> <summary>`，示例：`fix: chat 安卓端气泡间距`。
- PR 应包含：
  - 变更内容与原因
  - 影响模块/路径
  - 验证步骤（执行过的命令）
  - 前端改动的截图或 GIF

## 安全与配置建议
- 敏感信息放在 `.env`，禁止提交真实密钥。
- 新增配置项时同步更新 `.env.example`。
- 部署前检查 `deploy/` 中服务与反向代理配置是否匹配当前环境。
