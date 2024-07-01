import os
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskDetails(BaseModel):
    type: str
    params: dict


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = os.getenv("MODEL")
    messages: List[Message]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    stream: Optional[bool] = False
