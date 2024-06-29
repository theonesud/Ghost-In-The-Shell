import streamlit as st
from dotenv import load_dotenv
from ghost.routes.analyst import business_analyst
from ghost.routes.catalog import search_catalog
from ghost.routes.customer import customer_rep


def main():
    demos = ["Customer Service", "Product Search", "Business Analyst"]
    funcs = [customer_rep, search_catalog, business_analyst]
    if "demo" not in st.session_state:
        st.session_state.demo = demos[0]
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "seq_id" not in st.session_state:
        st.session_state.seq_id = 0

    with st.sidebar:
        selected = st.selectbox(
            "Choose an AI:",
            demos,
            index=demos.index(st.session_state.demo),
        )
        if selected != st.session_state.demo:
            st.session_state.demo = selected
            st.session_state.messages = []
            st.session_state.seq_id = 0

    # st.title("HumanCore AI")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Talk to the AI..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            resp = funcs[demos.index(st.session_state.demo)](
                prompt, st.session_state.messages
            )
            st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})


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


if __name__ == "__main__":
    # if not check_password():
    #     st.stop()
    main()
