import os
import pickle

import streamlit as st
from ghost.core.router import route
from ghost.routes.analyst import business_analyst
from ghost.routes.catalog import search_catalog
from ghost.routes.customer import customer_rep
from ghost.routes.intents import intents


def main():
    st.title("AI Terminal")
    if "intent_id" not in st.session_state:
        st.session_state.intent_id = None
    if "seq_id" not in st.session_state:
        st.session_state.seq_id = None
    choices = {
        1: {
            "target_func": search_catalog,
            "user_intent": "Search the product catalog",
        },
        2: {
            "target_func": business_analyst,
            "user_intent": "Talk to a business analyst",
        },
        3: {
            "target_func": customer_rep,
            "user_intent": "Talk to a customer representative",
        },
    }
    st.markdown(
        f"""Choose: {': '.join(f'{k}: {v['user_intent']}' for k, v in choices.items())}"""
    )
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Talk to the AI...."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = route(choices, prompt, st.session_state.messages)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


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
