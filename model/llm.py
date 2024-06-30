import instructor

from config import llm, model_name
from model.io import LLMResp


def generate(chat_history):
    return llm.chat.completions.create(
        model=model_name,
        temperature=0.1,
        response_model=instructor.Partial[LLMResp],
        messages=chat_history,
        stream=True,
    )
