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
