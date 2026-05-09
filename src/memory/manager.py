from dataclasses import dataclass, field

from memory.types import Dialogue, Dialogues

# 档位阈值
_FULL_LIMIT = 6  # ≤ 3 轮：原样
_WINDOW_LIMIT = 16  # ≤ 8 轮：保留首轮 + 最近 3 轮
_RECENT_ROUNDS = 3  # 保留的最近轮数


@dataclass
class DialogueManager:
    """对话管理器，按 thread_id 维护每个用户当前会话的历史对话 Dialogues 状态。"""

    _store: dict[str, Dialogues] = field(default_factory=dict)

    def register(self, thread_id: str) -> Dialogues:
        """请求入口显式初始化：首次出现的 thread_id 创建空 Dialogues，已存在则保留。"""
        if thread_id not in self._store:
            self._store[thread_id] = Dialogues(thread_id=thread_id, dialogues=[])
        return self._store[thread_id]

    def add_history(self, thread_id: str, query: str, content: str) -> None:
        """追加一轮对话：用户问句 + 角色回复。需先 register。"""
        self._store[thread_id].dialogues.extend([
            Dialogue(role="user", content=query),
            Dialogue(role="assistant", content=content),
        ])

    def load_history(self, thread_id: str) -> list[Dialogue]:
        """按对话量自动选择档位返回历史，兼顾上下文完整性与 token 成本。

        - n ≤ _FULL_LIMIT     : FULL 原样返回
        - n ≤ _WINDOW_LIMIT   : WINDOW 首轮 + 最近 _RECENT_ROUNDS 轮
        - 其它                : COMPACT 首轮 + 中段摘要 + 最近 _RECENT_ROUNDS 轮
        """
        dialogues = self._store[thread_id].dialogues
        # 保留的对话条数
        recent = _RECENT_ROUNDS * 2

        # 全部保留
        if len(dialogues) <= _FULL_LIMIT:
            return list(dialogues)

        head = list(dialogues[:2])  # 首部一轮
        tail = list(dialogues[-recent:])  # 尾部三轮

        # 保留首轮 + 最近若干轮
        if len(dialogues) <= _WINDOW_LIMIT:
            return head + tail

        # 取出首轮和尾部三轮以外的中间轮对话作为压缩对象
        middle_dialogues = dialogues[2:-recent]
        # 只取用户提问, 清理空白和换行, 每条问句截前 40 字符，避免输入太多token
        keypoints = [middle_dialogue.content.strip().replace("\n", " ")[:40]
                     for middle_dialogue in middle_dialogues if middle_dialogue.role == "user"]
        # 创建摘要对话
        summary = Dialogue(
            role="assistant",
            content=f"（早期 {len(middle_dialogues) // 2} 轮摘要｜用户曾问：{' / '.join(keypoints)}）",
        )
        return head + [summary] + tail

    def clear_history(self, thread_id: str) -> None:
        """清除指定会话的对话历史。"""
        self._store.pop(thread_id, None)


dialogue_manager = DialogueManager()
