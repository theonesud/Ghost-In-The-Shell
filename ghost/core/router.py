import asyncio

import streamlit as st
from ghost.routes.intents import *
from ghost.routes.intents import intents
from ghost.utils.openai import OpenAIChatLLM

intent_recognizer = OpenAIChatLLM()
asyncio.run(
    intent_recognizer.set_system_prompt(f"""Decide which intent to use in order to satisfy the user:
{intents}
Reply only the serial number of the intent.
""")
)


def route(prompt, messages):
    current_intent = int(asyncio.run(intent_recognizer(prompt)))
    if st.session_state.intent != current_intent:
        st.session_state.intent = current_intent
        st.session_state.pair_index = 0
    return globals()[f"reply_to_intent_{current_intent}"](prompt, messages)
