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
async def test_creative_writing():
    prompt = (
        "Write a blog post about artificial general intelligence taking over the world"
    )
    max_new_tokens = 2048
    text = await call_model(prompt, max_new_tokens, creative_writing_mode)
    print(text)


@pytest.mark.asyncio
async def test_no_bs_chat():
    prompt = "What did humans evolve from?"
    max_new_tokens = 2048
    text = await call_model(prompt, max_new_tokens, no_bs_chat_mode)
    print(text)


@pytest.mark.asyncio
async def test_balanced_chat():
    prompt = "What did humans evolve from?"
    max_new_tokens = 2048
    text = await call_model(prompt, max_new_tokens, balanced_chat_mode)
    print(text)


@pytest.mark.asyncio
async def test_code_writing():
    prompt = "Write a function that takes a list of numbers and returns the sum of all the numbers"
    max_new_tokens = 2048
    text = await call_model(prompt, max_new_tokens, code_writing_mode)
    print(text)


@pytest.mark.asyncio
async def test_deep_thinking():
    prompt = "What did humans evolve from?"
    max_new_tokens = 2048
    text = await call_model(prompt, max_new_tokens, deep_thinking_mode)
    print(text)
