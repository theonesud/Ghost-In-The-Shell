import streamlit as st
from ghost.core.router import intents, route


def main():
    st.title("Ghost in the Shell")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "intent" not in st.session_state:
        st.session_state.intent = ""
        st.session_state.pair_index = None
        usage = f"""### Choose your intent:
{intents}
        """
        st.markdown(usage)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("What would you like me do?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = route(prompt, st.session_state.messages)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


# import os
# import time

# from lib.pragma import reply

# os.makedirs("scrapes", exist_ok=True)


# if __name__ == "__main__":
#     start_time = time.time()
#     reply("https://inbox.logisy.tech/inbox/tickets/6766326")
#     print(f"Total time taken: {time.time() - start_time :.2f} seconds")


if __name__ == "__main__":
    # if not check_password():
    #     st.stop()
    main()
