import json
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = f"{os.getenv('UI_BACKEND')}/chat/completions"
API_KEY = os.getenv("OPENAI_API_KEY")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def get_chat_response(messages):
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


if prompt := st.chat_input("Sup?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_generator = get_chat_response(
            [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
        )
        response_text = st.write_stream(response_generator)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
