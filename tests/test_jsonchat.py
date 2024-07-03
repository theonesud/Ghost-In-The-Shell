import json
import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = f"{os.getenv('URL')}/json/chat/completions"
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
    for line in response.iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                line = line[6:]
            if line == "[DONE]":
                break
            try:
                response_data = json.loads(line)
                if not response_data:
                    break
                # response_text += response_data["choices"][0]["delta"]["content"]
                yield response_data
            except json.JSONDecodeError:
                continue
    # return response_data


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
    return response.json()


@pytest.fixture
def messages():
    return [{"role": "user", "content": "Hello, how are you?"}]


def test_get_resp(messages):
    response = get_resp(messages)
    assert isinstance(response, dict)
    assert len(response) > 0


def test_get_generator(messages):
    response_generator = get_generator(messages)
    response = list(response_generator)[-1]
    assert isinstance(response, dict)
    assert len(response) > 0
