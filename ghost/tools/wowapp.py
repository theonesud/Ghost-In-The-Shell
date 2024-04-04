import requests
import streamlit as st

# import wikipedia
from ai import call_ai

# from bs4 import BeautifulSoup
# from googlesearch import search
from ghost.utils.settings import sidebar

st.markdown("<h1 style='text-align: center;'>AI</h1>", unsafe_allow_html=True)


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    (
        infinite_chat_mode,
        model_options,
        temp_slider,
        grammar_correct_toggle,
        a1_c2_toggle,
        input_language,
        tone_persona_dropdown,
        metaprompt_toggle,
        audio_input_toggle,
        research_toggle,
        wikipedia_toggle,
        entity_recognition,
        synonym_toggle,
        antonym_toggle,
        etymologist_toggle,
        translation_options,
        sentiment_options,
        ascii_emotion_toggle,
        summary_toggle,
        audio_output_option,
        code_output_toggle,
        prd_before_coding_toggle,
        translation_options_code,
        documentation_toggle,
        bugfinder_toggle,
        improvement_suggestions_toggle,
    ) = sidebar()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if audio_input_toggle:
    st.info("Audio Input not supported yet")


# def search_wikipedia(query):
#     return wikipedia.summary(query)
#     page = wiki_wiki.page()
#     return page.summary  # or other page details


if prompt := st.chat_input(""):
    if grammar_correct_toggle:
        prompt = call_ai(
            "Grammar Corrected",
            f"You are an expert in {input_language}. I will give you a statement in {input_language}, you need to correct its grammar. Reply only with the corrected statement and nothing else",
            prompt,
            temp_slider,
        )
    if a1_c2_toggle:
        prompt = call_ai(
            "Improved Language",
            f"You are an expert in {input_language}. I will give you a statement in {input_language}, you need convert it from a level A1 to level C2 without changing its meaning. Reply only with the improved statement and nothing else.",
            prompt,
            temp_slider,
        )
    if metaprompt_toggle:
        prompt = call_ai(
            "Improved Prompt",
            "You are an expert in writing ChatGPT prompts. I'll provide you a prompt, you refine it such that ChatGPT gives a creative yet specific, deep yet concise reply. Reply with the refined prompt and nothing else",
            prompt,
            temp_slider,
        )
    if research_toggle:
        keywords = call_ai(
            "Search Keywords",
            "You are an expert in SEO. Given the following prompt, generate a list of SEO-friendly keywords. Reply with the keywords and nothing else",
            prompt,
            temp_slider,
        )
        search_results = search(keywords, num_results=2)
        summaries = []
        for result in search_results:
            page = requests.get(result)
            soup = BeautifulSoup(page.content, "html.parser")
            print(soup.text)
            summary = call_ai(
                "Research Summary",
                "You are an expert in summarizing a document. Use bullet points to go over all the important points, insights and details in the document. Reply with the summary and nothing else",
                soup.text,
                temp_slider,
            )
            summaries.append(summary)
    # if wikipedia_toggle:
    #     try:
    #         res = search_wikipedia(prompt)
    #     except:
    #         res = "No results found"

    call_ai("", None, prompt, temp_slider, append_to_chat=True)
