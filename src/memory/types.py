from dataclasses import dataclass


@dataclass(frozen=True)
class Dialogue:
    """对话历史记录."""
    role: str
    content: str


@dataclass(frozen=True)
class Dialogues:
    """多轮对话历史记录."""
    thread_id: str # 会话ID
    dialogues: list[Dialogue] # 当前会话的对话历史记录列表
