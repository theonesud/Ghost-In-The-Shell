import asyncio

import streamlit as st
from ghost.utils.openai import OpenAIChatLLM

ai = OpenAIChatLLM()


def reply_to_intent_5(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Enter Customer Query (Non-English) Example: ¿Cuándo llegará mi pedido?"
    elif st.session_state.pair_index == 1:
        translator = OpenAIChatLLM()
        asyncio.run(translator.set_system_prompt("Translate this text to english"))
        translation = asyncio.run(translator(prompt))
        st.write(translation)
        responder = OpenAIChatLLM()
        asyncio.run(responder.set_system_prompt("Respond to the users query normally"))
        response = asyncio.run(responder(translation))
        st.write(response)
        translator = OpenAIChatLLM()
        asyncio.run(
            translator.set_system_prompt(
                "Translate the response to the original qeustions language"
            )
        )
        translation = asyncio.run(
            translator(f"Response: {response}. Original question: {prompt}")
        )
        return translation


def reply_to_intent_6(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Enter Customer Segment"
    elif st.session_state.pair_index == 1:
        translator = OpenAIChatLLM()
        asyncio.run(
            translator.set_system_prompt(
                f"Create a personalized email for the customer segment: {prompt}."
            )
        )
        translation = asyncio.run(translator(prompt))
        return translation


def reply_to_intent_7(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Enter Topic"
    elif st.session_state.pair_index == 1:
        translator = OpenAIChatLLM()
        asyncio.run(
            translator.set_system_prompt(
                f"Generate an engaging twitter post for the following prompt: {prompt}"
            )
        )
        translation = asyncio.run(translator(prompt))
        return translation
