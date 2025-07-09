from agents.memory.message import Message
from typing import List
from datetime import datetime
import uuid

class Thread:
    def __init__(self, id: str, messages: List[Message]):
        self.id = id
        self.messages = messages

    def add_user_message(self, content: str):
        self.messages.append(
            Message(
                id=str(uuid.uuid4()),
                role="user",
                content=content,
                timestamp=datetime.utcnow()
            )
        )

    def add_agent_message(self, content: str):
        self.messages.append(
            Message(
                id=str(uuid.uuid4()),
                role="assistant",
                content=content,
                timestamp=datetime.utcnow()
            )
        )

    def to_openai_format(self):
        return [{"role": m.role, "content": m.content} for m in self.messages]
