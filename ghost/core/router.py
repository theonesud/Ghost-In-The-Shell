import asyncio

import streamlit as st
from ghost.routes.intents import *
from ghost.routes.intents import intents
from ghost.utils.openai import OpenAIChatLLM

intent_recognizer = OpenAIChatLLM()
asyncio.run(
    intent_recognizer.set_system_prompt(f"""Which of the following intents is the user trying to do? Only reply with the serial number:
{intents}
Only reply with the serial number.
""")
)


def route(prompt, messages):
    if not st.session_state.intent:
        current_intent = int(asyncio.run(intent_recognizer(prompt)))
        # if st.session_state.intent != current_intent:
        st.session_state.intent = current_intent
        st.session_state.pair_index = 0
        st.session_state.subpair_index = 0
    return globals()[f"reply_to_intent_{st.session_state.intent}"](prompt, messages)
