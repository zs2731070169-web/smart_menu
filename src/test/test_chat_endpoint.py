"""
/chat 接口回归测试。

策略：
- 使用 FastAPI TestClient + 签名 cookie 会话；
- mock `service.menu.handle_chat`，避免依赖真实 LLM / Pinecone / 高德 API；
- 覆盖正常文本回复、结构化数据回复、空查询、会话保持、异常降级、/new/chat 重置等场景。
"""
import pytest

from agent.chat_engine import ChatResponse


@pytest.fixture
def patch_handle_chat(monkeypatch):
    """
    返回一个工厂函数，调用时把 service.menu.handle_chat 替换为返回指定 ChatResponse 的桩。
    同时记录每次调用的入参，便于断言。
    """

    def _apply(response: ChatResponse | Exception):
        calls: list[tuple[str, str]] = []

        async def _stub(query: str, thread_id: str):
            calls.append((query, thread_id))
            if isinstance(response, Exception):
                raise response
            return response

        # 注意：必须 patch service.menu 命名空间下的引用，因为 routes 通过 service.menu.chat 间接调用
        monkeypatch.setattr("service.menu.handle_chat", _stub)
        return calls

    return _apply


# ---------------------------------------------------------------------------
# 正常路径
# ---------------------------------------------------------------------------

def test_chat_returns_text_reply(client, patch_handle_chat):
    """LLM 直答路径：仅有 message 字段，data 为空。"""
    calls = patch_handle_chat(ChatResponse(success=True, message="您好，营业时间 9:00-22:00"))

    resp = client.get("/chat", params={"query": "你们几点关门"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] is True
    assert body["message"] == "您好，营业时间 9:00-22:00"
    assert body["data"] is None
    assert len(calls) == 1
    assert calls[0][0] == "你们几点关门"
    # 自动分配的 session_id 应为非空字符串
    assert calls[0][1]


def test_chat_returns_structured_data(client, patch_handle_chat):
    """工具返回结构化数据路径：data 字段携带菜品/配送等信息。"""
    payload = {
        "menus": [{"id": 1, "dish_name": "宫保鸡丁"}],
        "reply": "为您推荐宫保鸡丁",
    }
    patch_handle_chat(ChatResponse(success=True, data=payload))

    resp = client.get("/chat", params={"query": "推荐一道川菜"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] is True
    assert body["data"] == payload


# ---------------------------------------------------------------------------
# 入参边界
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("query", ["", "   "])
def test_chat_empty_query_passthrough(client, patch_handle_chat, query):
    """
    空字符串/纯空白 query：路由本身不拦截，应交由 chat_engine 决定。
    这里通过 stub 验证 query 被原样透传。
    """
    calls = patch_handle_chat(
        ChatResponse(success=False, message="抱歉，我没有收到您的查询，请您再试一次。")
    )

    resp = client.get("/chat", params={"query": query})

    assert resp.status_code == 200
    body = resp.json()
    # 路由对 ChatResponse(success=False) 仍返回 status=True（因为没抛异常）；
    # 业务层成功/失败由 message 体现。锁定当前实现的契约。
    assert body["status"] is True
    assert body["message"] == "抱歉，我没有收到您的查询，请您再试一次。"
    assert calls[0][0] == query


def test_chat_default_query_when_param_missing(client, patch_handle_chat):
    """未传 query 参数时，FastAPI 默认值为空字符串。"""
    calls = patch_handle_chat(ChatResponse(success=False, message="抱歉，我没有收到您的查询，请您再试一次。"))

    resp = client.get("/chat")

    assert resp.status_code == 200
    assert calls[0][0] == ""


# ---------------------------------------------------------------------------
# 会话（session）行为
# ---------------------------------------------------------------------------

def test_chat_session_id_persists_across_requests(client, patch_handle_chat):
    """同一 client（共享 cookie）多次请求应使用同一 session_id。"""
    calls = patch_handle_chat(ChatResponse(success=True, message="ok"))

    client.get("/chat", params={"query": "你好"})
    client.get("/chat", params={"query": "再问一句"})

    assert len(calls) == 2
    assert calls[0][1] == calls[1][1]
    assert calls[0][1]  # 非空


def test_new_chat_resets_session(client, patch_handle_chat):
    """/new/chat 删除 session_id 后，下一次 /chat 应分配到新的 thread_id。"""
    calls = patch_handle_chat(ChatResponse(success=True, message="ok"))

    client.get("/chat", params={"query": "第一次"})
    first_session = calls[-1][1]

    reset = client.post("/new/chat")
    assert reset.status_code == 200
    assert reset.json() is True

    client.get("/chat", params={"query": "重置后第一次"})
    second_session = calls[-1][1]

    assert first_session and second_session
    assert first_session != second_session


def test_independent_clients_have_distinct_sessions(app, patch_handle_chat):
    """不同 TestClient 实例（不同浏览器）之间会话隔离。"""
    from fastapi.testclient import TestClient
    calls = patch_handle_chat(ChatResponse(success=True, message="ok"))

    with TestClient(app) as c1, TestClient(app) as c2:
        c1.get("/chat", params={"query": "客户端1"})
        c2.get("/chat", params={"query": "客户端2"})

    sessions = {c[1] for c in calls}
    assert len(sessions) == 2


# ---------------------------------------------------------------------------
# 异常降级
# ---------------------------------------------------------------------------

def test_chat_handles_internal_exception_gracefully(client, patch_handle_chat):
    """
    handle_chat 抛出未捕获异常时，路由层 try/except 兜底，
    应返回 status=False 且带友好提示，HTTP 状态码仍为 200。
    """
    patch_handle_chat(RuntimeError("boom"))

    resp = client.get("/chat", params={"query": "随便问点啥"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] is False
    assert "聊天服务发生错误" in body["message"]


def test_chat_business_failure_keeps_status_true(client, patch_handle_chat):
    """
    业务层判定失败（ChatResponse.success=False）但未抛异常时，
    路由直接透传 message，status 仍为 True（按 service.chat 的当前实现）。
    """
    patch_handle_chat(ChatResponse(success=False, message="抱歉，处理您的查询时发生了错误，请稍后再试。"))

    resp = client.get("/chat", params={"query": "异常工具调用"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] is True
    assert "请稍后再试" in body["message"]


# ---------------------------------------------------------------------------
# 关键词降级单元测试（chat_engine._fallback）
# ---------------------------------------------------------------------------

class TestFallbackRouting:
    """LLM 异常时的关键词降级路径，纯函数级别校验，不需要 HTTP。"""

    def test_delivery_keyword_routes_to_delivery_check(self):
        from agent.chat_engine import _fallback
        out = _fallback("外卖能送到我家吗？地址是上海市浦东新区世纪大道100号。")
        assert out["tool_name"] == "delivery_check"
        assert "上海市浦东新区世纪大道100号" in out["arguments"]["query"]

    def test_menu_keyword_routes_to_menu_inquiry(self):
        from agent.chat_engine import _fallback
        out = _fallback("有什么招牌菜推荐？")
        assert out["tool_name"] == "menu_inquiry"
        assert "招牌菜" in out["arguments"]["query"]

    def test_unrelated_query_returns_reply_only(self):
        from agent.chat_engine import _fallback
        out = _fallback("明天天气怎么样？")
        assert "tool_name" not in out
        assert "reply" in out and out["reply"]
