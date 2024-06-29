import dspy
import pytest

from config import (
    balanced_chat_mode,
    call_model,
    code_writing_mode,
    creative_writing_mode,
    deep_thinking_mode,
    no_bs_chat_mode,
)


@pytest.mark.asyncio
async def test_code_writing():
    prompt = "Write a function that takes a list of numbers and returns the sum of all the numbers"
    max_new_tokens = 2048
    text = await call_model(prompt, max_new_tokens, code_writing_mode)
    print(text)
