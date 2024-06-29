import asyncio

import streamlit as st
from ghost.routes.analyst import business_analyst
from ghost.routes.catalog import search_catalog
from ghost.routes.customer import customer_rep

# from ghost.routes.intents import *
from ghost.routes.intents import intents
from ghost.utils.openai import OpenAIChatLLM


def choose_intent(choices, prompt):
    ai = OpenAIChatLLM()
    asyncio.run(
        ai.set_system_prompt(
            f"Recognize the intent of the user. He has the list of intents. Only reply with the serial number of the intent that the user wants to choose: {': '.join(f'{k}: {v['user_intent']}' for k, v in choices.items())}"
        )
    )
    resp = asyncio.run(ai(prompt))
    return int(resp)


def route(choices, prompt, messages):
    if not st.session_state.intent_id:
        st.session_state.intent = choose_intent(choices, prompt)
    return choices[st.session_state.intent]["target_func"](prompt, messages)
    # current_intent = int(asyncio.run(intent_recognizer(prompt)))
    # if st.session_state.intent != current_intent:
    # st.session_state.intent = current_intent
    #     st.session_state.pair_index = 0
    # return globals()[f"reply_to_intent_{current_intent}"](prompt, messages)
