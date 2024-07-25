from typing import List

class LLMMessage:
    def __init__(self, role: str, timestamp: str, content: str):
        self.role = role
        self.timestamp = timestamp
        self.content = content

class LLMContext:
    def __init__(self, thread_id: str, messages: List[LLMMessage]):
        self.thread_id = thread_id
        self.messages = messages
