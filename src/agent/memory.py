import threading
from collections import defaultdict


class Memory:
    def __init__(self):
        # 使用线程安全的方式管理对话缓存
        self._lock = threading.RLock()
        self.memory = defaultdict(list)

    def add(self, thread_id: str, query, content, role: str):
        conversation = {
            "query": query,
            f"{role}_answer": content
        }
        with self._lock:
            self.memory[thread_id].append(conversation)

    def recall(self, thread_id: str) -> list[dict]:
        with self._lock:
            return list(self.memory.get(thread_id, []))

    def clear(self, thread_id: str):
        with self._lock:
            self.memory.pop(thread_id, None)

    def __len__(self):
        with self._lock:
            return len(self.memory)

    def __str__(self):
        with self._lock:
            return str(dict(self.memory))


memory = Memory()