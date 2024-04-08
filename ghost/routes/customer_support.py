import asyncio

import streamlit as st
from ghost.utils.openai import OpenAIChatLLM

translator1 = OpenAIChatLLM()
asyncio.run(translator1.set_system_prompt("Translate this text to english"))

responder = OpenAIChatLLM()
asyncio.run(responder.set_system_prompt("Respond to the users query normally"))
translator2 = OpenAIChatLLM()
asyncio.run(
    translator2.set_system_prompt(
        "Translate the response to the original qeustions language"
    )
)
emailer = OpenAIChatLLM()
asyncio.run(
    emailer.set_system_prompt(
        "Create a personalized email for the user mentioned customer segment"
    )
)
tweeter = OpenAIChatLLM()
asyncio.run(
    tweeter.set_system_prompt(
        "Generate an engaging twitter post based on the user's usecase. Do not use hashtags. The post should be relavent to the user's query and provide great value"
    )
)


def reply_to_intent_5(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Enter Customer Query (Non-English) Example: ¿Cuándo llegará mi pedido?"
    elif st.session_state.pair_index == 1:
        translation = asyncio.run(translator1(prompt))
        st.write(translation)
        response = asyncio.run(responder(translation))
        st.write(response)
        translation = asyncio.run(
            translator2(f"Response: {response}. Original question: {prompt}")
        )
        return translation


def reply_to_intent_6(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Enter Customer Segment"
    elif st.session_state.pair_index == 1:
        translation = asyncio.run(emailer(prompt))
        return translation


def reply_to_intent_7(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Enter Topic"
    elif st.session_state.pair_index == 1:
        translation = asyncio.run(tweeter(prompt))
        return translation
