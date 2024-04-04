import streamlit as st
from ghost.core.router import route
from ghost.utils.openai import OpenAIChatLLM

st.title("Ghost in the Shell")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "intent" not in st.session_state:
    st.session_state.intent = ""
    usage = """Choose your intent:
    - Talk to a customer service representative
    - Talk to a business analyst
    """
    st.markdown(usage)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
ai = OpenAIChatLLM()
if prompt := st.chat_input("What would you like me do?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = route(ai, prompt, st.session_state.messages)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


# import os
# import time

# from lib.pragma import reply

# os.makedirs("scrapes", exist_ok=True)


# if __name__ == "__main__":
#     start_time = time.time()
#     reply("https://inbox.logisy.tech/inbox/tickets/6766326")
#     print(f"Total time taken: {time.time() - start_time :.2f} seconds")
