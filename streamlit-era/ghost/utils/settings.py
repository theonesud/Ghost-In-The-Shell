import streamlit as st


def sidebar():
    st.markdown(
        "<h2 style='text-align: center; font-weight: bold;'>🌐 Global Settings</h2>",
        unsafe_allow_html=True,
    )
    infinite_chat_mode = st.checkbox("Infinite Chat Mode", value=True)

    st.markdown("---")  # Separator

    st.markdown(
        "<h2 style='text-align: center; font-weight: bold;'>📝 Input Settings</h2>",
        unsafe_allow_html=True,
    )

    # st.markdown("##### Text Input")
    model_options = st.selectbox(
        "Model Options",
        [
            "gpt-3.5-turbo-1106",
            "gpt-4-vision-preview",
            "gpt-4-1106-preview",
            "dall-e-3",
            "tts-1",
            "tts-1-hd",
        ],
    )
    st.session_state["openai_model"] = model_options

    input_language = st.selectbox(
        "Input Language (For auto correct grammar and improve language level)",
        ["english", "spanish", "hindi"],
    )
    tone_persona_dropdown = st.selectbox(
        "Persona",
        [
            "Helpful Assistant",
        ],
    )

    temp_slider = st.slider("Temperature", 0.0, 1.0, 0.7)
    grammar_correct_toggle = st.checkbox("Auto Correct Grammar", value=False)
    a1_c2_toggle = st.checkbox("Improve Language Level", value=False)
    metaprompt_toggle = st.checkbox("Metaprompting On/Off", value=False)
    audio_input_toggle = st.checkbox("Audio Input On/Off", value=False)

    st.markdown("---")  # Separator

    st.markdown(
        "<h2 style='text-align: center; font-weight: bold;'>💬 Output Settings</h2>",
        unsafe_allow_html=True,
    )
    research_toggle = st.checkbox("Research Online Before Answering", value=True)
    wikipedia_toggle = st.checkbox("Get Wiki Summary", value=True)
    entity_recognition = st.checkbox("Entities Recognition", value=False)
    synonym_toggle = st.checkbox("Show Synonyms for Entities", value=False)
    antonym_toggle = st.checkbox("Show Antonyms for Entities", value=False)
    etymologist_toggle = st.checkbox("Etymologist for Entities", value=False)
    translation_options = st.selectbox("Translation Options", ["Auto", "Manual"])
    sentiment_options = st.selectbox(
        "Sentiment Options", ["Positive", "Negative", "Neutral"]
    )
    ascii_emotion_toggle = st.checkbox("Ascii Emotion", value=False)
    summary_toggle = st.checkbox("Show Summary", value=False)

    audio_output_option = st.radio(
        "Audio Output", ["Normal Output", "Translation", "Summary"], index=0
    )

    st.markdown("---")  # Separator

    st.markdown(
        "<h2 style='text-align: center; font-weight: bold;'>💻 Code Output</h2>",
        unsafe_allow_html=True,
    )
    code_output_toggle = st.checkbox("Code Output On/Off", value=True)
    prd_before_coding_toggle = st.checkbox("Create PRD Before Coding", value=False)
    translation_options_code = st.selectbox(
        "Translation Options (Library/Language)", ["Python", "JavaScript", "C++"]
    )
    documentation_toggle = st.checkbox("Documentation", value=False)
    bugfinder_toggle = st.checkbox("Bugfinder", value=False)
    improvement_suggestions_toggle = st.checkbox("Improvement Suggestions", value=False)

    return (
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
    )
