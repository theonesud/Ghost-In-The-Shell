def respond(prompt, chat_history):
    if prompt.startswith("@"):
        return write_code(prompt, chat_history)
    elif len(chat_history) > 2 and not chat_history[-2]["content"].startswith("#prd"):
        return create_prd(chat_history)
    elif prompt.startswith("#prd"):
        ask_prd_questions(chat_history)
    else:
        return ai(
            "You are a god, only respond as someone who knows the entire existence",
            chat_history,
        )
