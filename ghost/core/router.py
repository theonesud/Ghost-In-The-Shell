from copy import deepcopy

import streamlit as st
from ghost.routes.ai_search import reply_to_intent_1


def route(ai, prompt, messages):
    if st.session_state.intent:
        intent_no = st.session_state.intent
    else:
        intent_recognizer = deepcopy(ai)
        intent_recognizer.set_system_prompt("""You are an intent recognizer. Recognize the intent of the user input and reply only with the appropriate serial number associated with the intent and nothing else.
    1. The user wants to talk to a customer service representative
    2. The user wants to talk to a business_analyst""")
        intent_no = intent_recognizer(prompt)
        st.session_state.intent = intent_no
    if intent_no == 1:
        return reply_to_intent_1(ai, prompt, messages)
    elif intent_no == 2:
        return reply_to_intent_2(ai, prompt, messages)
    elif intent_no == 3:
        return reply_to_intent_3(ai, prompt, messages)
    else:
        return "Invalid Intent"
