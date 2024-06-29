import json
import pprint

import pytest
from httpx import AsyncClient

from main import app

chat_id = None


@pytest.mark.asyncio
async def test_stream_json_data():
    global chat_id

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/chats/generate_response/0",
            json={"input_prompt": "Who is the president of USA?"},
        )
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line.strip():
                data = json.loads(line)
                chat_id = data["chat_id"]
                content = data["content"]
                sentiment = data["sentiment"]
                print(f"{content} [{sentiment}]")

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            f"/chats/generate_response/{chat_id}",
            json={"input_prompt": "What is its capital?"},
        )
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line.strip():
                data = json.loads(line)
                chat_id = data["chat_id"]
                content = data["content"]
                sentiment = data["sentiment"]
                print(f"{content} [{sentiment}]")


@pytest.mark.asyncio
async def test_get_chats():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/chats/")
        assert response.status_code == 200
        pprint.pprint(response.json())


@pytest.mark.asyncio
async def test_get_chat():
    global chat_id

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/chats/{chat_id}")
        assert response.status_code == 200
        pprint.pprint(response.json())
