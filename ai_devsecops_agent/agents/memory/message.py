from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    id: str
    role: str  # "user" or "agent"
    content: str
    timestamp: datetime
