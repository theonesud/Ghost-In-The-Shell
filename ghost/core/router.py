import asyncio

import streamlit as st
from ghost.routes.ai_search import reply_to_intent_1, reply_to_intent_2
from ghost.routes.assistant import reply_to_intent_3, reply_to_intent_4
from ghost.routes.automaton import reply_to_intent_9
from ghost.routes.customer_support import (
    reply_to_intent_5,
    reply_to_intent_6,
    reply_to_intent_7,
)
from ghost.routes.download import reply_to_intent_8
from ghost.routes.personas import reply_to_intent_10
from ghost.utils.openai import OpenAIChatLLM

intents = """
1. The user wants to Search by Vibe from a ecom catalog
2. The user wants to Ask a business question to a sales database
3. The user wants to use the python template to create a new fastapi server
4. The user wants to create a prd for backend team
5. The user wants to talk to a regional customer support representative
6. The user wants to create a personalized email for a customer segment
7. The user wants to create a twitter post for a topic
8. The user wants to download some urls
9. The user wants to talk to the automaton
10. The user wants to talk to a specific persona
"""
intent_recognizer = OpenAIChatLLM()
asyncio.run(
    intent_recognizer.set_system_prompt(f"""You are an intent recognizer. Recognize the intent of the user input and reply only with the appropriate serial number associated
with the intent
{intents}
""")
)


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
        intent_no = int(asyncio.run(intent_recognizer(prompt)))
        st.session_state.intent = intent_no
        st.session_state.pair_index = 0
    # print(f"?????????????????????????Intent: {intent_no}, {type(intent_no)}")
    return globals()[f"reply_to_intent_{intent_no}"](prompt, messages)
    # try:
    #     reply_function = globals().get(f"reply_to_intent_{intent_no}")
    #     if reply_function:
    #         return reply_function(prompt, messages)
    #     else:
    #         raise ValueError(f"No function found for intent number: {intent_no}")
    # except Exception as e:
    #     return str(e)
