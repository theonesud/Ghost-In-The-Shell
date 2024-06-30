import json

import requests
import streamlit as st

# Streamlit page configuration
st.set_page_config(page_title="Chat with API", layout="wide")

# Backend API URL
api_url = "http://localhost:8000/chats"

# Streamlit sidebar for user input
st.title("Query the API")
user_input = st.text_input("Enter your message:", "")
button_sent = st.button("Send")

# Streamlit container to show responses
response_container = st.empty()


# Function to stream messages from the API
def stream_messages(chat_id, message):
    if chat_id is None:
        endpoint = f"{api_url}/generate_response/0"
    else:
        endpoint = f"{api_url}/generate_response/{chat_id}"

    with requests.post(
        endpoint, json={"input_prompt": message}, stream=True
    ) as response:
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    response_container.write(f"{data['content']} [{data['sentiment']}]")
                    chat_id = data["chat_id"]
        else:
            st.error("Failed to get response from the API")
    return chat_id


# Session state to store chat ID
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

# Handle button press
if button_sent and user_input:
    st.session_state.chat_id = stream_messages(st.session_state.chat_id, user_input)

# Displaying ongoing conversation
if st.session_state.chat_id:
    st.write(f"Conversation ID: {st.session_state.chat_id}")
