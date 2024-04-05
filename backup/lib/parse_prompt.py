import os
from pathlib import Path

from lib.openai import ai, ai_create_code


def write_code(prompt, chat_history):
    # usage: @py/api/route.py create a route file and connect it to main.py
    folder = prompt[1:4].lower()
    cmd = prompt.split(" ")[0][4:]
    with open(Path(f"sop/{folder}/{cmd}")) as f:
        code = f.read()
    generated_code, file_location = ai_create_code(
        "Edit this template according to the user's needs. Follow the template closely and add all the features to it without the user specifying. Be very mindful of the usecase the user is trying to achieve.",
        chat_history,
        code,
    )
    os.makedirs("output", exist_ok=True)
    file_location_path = Path(file_location)
    generated_loc = Path("output") / file_location_path
    generated_loc.parent.mkdir(parents=True, exist_ok=True)
    with open(generated_loc, "w") as f:
        f.write(generated_code)
    return f"```python\n{generated_code}\n```"


def create_prd(chat_history):
    with open(Path("sop/prd.md"), "r") as f:
        prd = f.read()
    generated_prd = ai(
        f"Create a PRD based on the given structure and the user's requirements. It should have details about the database structure, route structure, implementation details, any special requirements. Example PRD Structure: {prd}",
        chat_history,
    )
    with open(Path("output/prd.md"), "w") as f:
        f.write(generated_prd)
    return generated_prd


def ask_prd_questions(chat_history):
    with open(Path("sop/prd.md"), "r") as f:
        prd = f.read()
    return ai(
        f"Your job is to create a set of questions for the user. From the answers of the questions you should be able to create a PRD like the one I've mentioned below. Ask very specific questions to the user. You should have details about the database structure, route structure, implementation details, any special requirements. Example PRD: {prd}",
        chat_history,
    )


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
