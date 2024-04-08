import asyncio

import streamlit as st
from ghost.schema.persona import Persona
from ghost.utils.openai import OpenAIChatLLM

persona = OpenAIChatLLM()


def reply_to_intent_10(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return f"Enter a persona code to run: {[member.name for member in Persona]}"
    elif st.session_state.pair_index == 1:
        print(Persona._member_map_[prompt])
        asyncio.run(persona.set_system_prompt(Persona._member_map_[prompt].value))
        # meta = asyncio.run(persona(prompt))
        st.session_state.pair_index = 2
        return f"Hi, I am a {prompt}. What would you like me to do?"
    elif st.session_state.pair_index == 2:
        meta = asyncio.run(persona(prompt))
        return meta


# midprompt = OpenAIChatLLM()
# asyncio.run(
#     midprompt.set_system_prompt(
#         "You are an expert in writing prompts for an AI Image Generator. I'll provide you a prompt, you refine it such that the AI creates a detailed, creative, and unique image. Use specific keywords to improve lighting, shadows, colors, textures, shapes, artist style, image style, realism level, etc. Reply with the refined prompt and nothing else"
#     )
# )


# def reply_to_intent_11(prompt, messages):
#     if st.session_state.pair_index == 0:
#         st.session_state.pair_index = 1
#         return "Enter an image prompt you want to improve"
#     elif st.session_state.pair_index == 1:
#         meta = asyncio.run(midprompt(prompt))
#         return meta
