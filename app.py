import os
import pickle

import streamlit as st
from ghost.core.router import intents, route


def main():
    st.title("Ghost in the Shell")

    # file_path = os.path.join(os.getcwd(), "ghost.pkl")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
    #     with open(file_path, "rb") as f:
    #         st.session_state.messages = pickle.load(f)
    # else:
    #     with open(file_path, "wb") as f:
    #         pickle.dump(st.session_state.messages, f)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if "intent" not in st.session_state:
        st.session_state.intent = ""
        st.session_state.pair_index = None
        usage = f"""### What do you want to do?
{intents}
        """
        st.markdown(usage)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("What would you like me do?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = route(prompt, st.session_state.messages)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    # with open(os.path.join(os.getcwd(), "ghost.pkl"), "wb") as f:
    #     pickle.dump(st.session_state.messages, f)


def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if __name__ == "__main__":
    # if not check_password():
    #     st.stop()
    main()
