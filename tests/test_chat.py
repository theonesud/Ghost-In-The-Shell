import json

import pytest
from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_stream_json_data():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/chats/generate_response/0",
            json={"input_prompt": "What is the purpose of life according to you?"},
        )
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line.strip():
                data = json.loads(line)
                chat_id = data["chat_id"]
                content = data["content"]
                sentiment = data["sentiment"]
                print(f"Chat ID: {chat_id}, Content: {content}, Sentiment: {sentiment}")
