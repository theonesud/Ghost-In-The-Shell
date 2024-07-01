import os
from typing import List, Optional

from pydantic import BaseModel, Field

# class InputPrompt(BaseModel):
#     input_prompt: str


# class LLMResp(BaseModel):
#     content: str = Field(description="The content of the reply")  # Do not change this
#     sentiment: str = Field(description="The sentiment of the reply")


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
