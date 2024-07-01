import json
import os

import pytest
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
API_URL = f"{os.getenv('UI_BACKEND')}/chat/completions"
API_KEY = os.getenv("OPENAI_API_KEY")


def get_generator(messages):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": os.getenv("MODEL"),
        "messages": messages,
        "stream": True,
    }

    response = requests.post(
        API_URL, headers=headers, data=json.dumps(data), stream=True
    )

    response_text = ""
    for line in response.iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                line = line[6:]
            if line == "[DONE]":
                break
            try:
                response_data = json.loads(line)
                if not response_data["choices"][0]["delta"]:
                    break
                response_text += response_data["choices"][0]["delta"]["content"]
                yield response_data["choices"][0]["delta"]["content"]
            except json.JSONDecodeError:
                continue

    return response_text


def get_resp(messages):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": os.getenv("MODEL"),
        "messages": messages,
        "stream": False,
    }
    response = requests.post(
        API_URL, headers=headers, data=json.dumps(data), stream=False
    )
    return response.json()["choices"][0]["message"]["content"]


@pytest.fixture
def messages():
    return [{"role": "user", "content": "Hello, how are you?"}]


def test_get_resp(messages):
    response = get_resp(messages)

    assert isinstance(response, str)
    assert len(response) > 0


def test_get_generator(messages):
    response_generator = get_generator(messages)
    response_text = "".join(list(response_generator))

    assert isinstance(response_text, str)
    assert len(response_text) > 0


# @pytest.mark.asyncio
# async def test_get_chats():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.get("/chats/")
#         assert response.status_code == 200
#         pprint.pprint(response.json())


# @pytest.mark.asyncio
# async def test_get_chat():
#     global chat_id

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.get(f"/chats/{chat_id}")
#         assert response.status_code == 200
#         pprint.pprint(response.json())
