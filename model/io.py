from pydantic import BaseModel, Field


class InputPrompt(BaseModel):
    input_prompt: str


class LLMResp(BaseModel):
    content: str = Field(description="The content of the reply")  # Do not change this
    sentiment: str = Field(description="The sentiment of the reply")
