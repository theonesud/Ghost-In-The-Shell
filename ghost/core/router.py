import asyncio

import streamlit as st
from ghost.routes.ai_search import reply_to_intent_1, reply_to_intent_2
from ghost.routes.assistant import reply_to_intent_3, reply_to_intent_4
from ghost.routes.customer_support import (
    reply_to_intent_5,
    reply_to_intent_6,
    reply_to_intent_7,
)
from ghost.routes.download import reply_to_intent_8
from ghost.utils.openai import OpenAIChatLLM


def route(prompt, messages):
    """
    Determines the intent of the user's input and returns the appropriate response.

    Args:
        ai (object): The AI model to use for intent recognition.
        prompt (str): The user's input prompt.
        messages (list): A list of previous messages in the conversation.

    Returns:
        str: The appropriate response based on the recognized intent, or "Invalid Intent" if the intent is not recognized.
    """
    if st.session_state.intent:
        intent_no = st.session_state.intent
    else:
        intent_recognizer = OpenAIChatLLM()
        asyncio.run(
            intent_recognizer.set_system_prompt("""You are an intent recognizer. Recognize the intent of the user input and reply only with the appropriate serial number associated with the intent and nothing else.
1. The user wants to Search by Vibe from a ecom catalog
2. The user wants to Ask a business question to a sales database
3. The user wants to use the python template to create a new fastapi server
4. The user wants to create a prd for backend team
5. The user wants to talk to a regional customer support representative
6. The user wants to create a personalized email for a customer segment
7. The user wants to create a twitter post for a topic
8. The user wants to download some urls
""")
        )
        intent_no = int(asyncio.run(intent_recognizer(prompt)))
        st.session_state.intent = intent_no
        st.session_state.pair_index = 0
    if intent_no == 1:
        return reply_to_intent_1(prompt, messages)
    elif intent_no == 2:
        return reply_to_intent_2(prompt, messages)
    elif intent_no == 3:
        return reply_to_intent_3(prompt, messages)
    elif intent_no == 4:
        return reply_to_intent_4(prompt, messages)
    elif intent_no == 5:
        return reply_to_intent_5(prompt, messages)
    elif intent_no == 6:
        return reply_to_intent_6(prompt, messages)
    elif intent_no == 7:
        return reply_to_intent_7(prompt, messages)
    elif intent_no == 8:
        return reply_to_intent_8(prompt, messages)
    else:
        return "Invalid Intent"
