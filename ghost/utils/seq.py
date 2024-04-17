import streamlit as st


def execute_tasks(prompt, task_list):
    if "pair_index" not in st.session_state:
        st.session_state.pair_index = 0

    current_task = task_list[st.session_state.pair_index]
    result = current_task(prompt) if callable(current_task) else current_task

    st.session_state.pair_index += 1  # Move to the next task
    if st.session_state.pair_index >= len(task_list):
        st.session_state.pair_index = 0  # Reset or handle completion

    return result

    # def task_0():
    #     # Task 0 - Choose a Language
    #     return "Choose a language - Urdu, Gujarati, Latvian"

    # def task_1(prompt):
    #     # Task 1 - Process Language Choice
    #     lang = process.extractOne(
    #         prompt, ["Urdu", "Gujarati", "Latvian"], scorer=fuzz.ratio
    #     )
    #     _map = {"Urdu": "ur", "Gujarati": "gu", "Latvian": "lv"}
    #     lang_code = _map[lang[0]]
    #     language_responses = {
    #         "ur": "میں آپ کی کیسے مدد کر سکتا ہوں",
    #         "gu": "હું આપની શું મદદ કરી શકું",
    #         "lv": "kā es varu Jums palīdzēt?",
    #     }
    #     return language_responses[lang_code]

    # def task_2(prompt, lang):
    #     # Task 2 - Translate and Handle Intent
    #     import asyncio

    #     translation = translate_text(prompt, lang, "en")
    #     subintent_no = asyncio.run(support_intent_recognizer(translation))
    #     st.write(translation)
    #     return subintent_no

    # # Example usage
    # result = execute_tasks(prompt, [task_0, task_1, task_2])
    # st.write(result)
