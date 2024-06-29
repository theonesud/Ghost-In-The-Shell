import json

import pytest
from httpx import AsyncClient

from main import app  # Adjust this import based on your file structure


@pytest.mark.asyncio
async def test_stream_json_data():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "chats/generate_response/0",
            json={"input_prompt": "Tell me a joke."},
        )

        async for line in response.aiter_lines():
            print("---------", (line))
