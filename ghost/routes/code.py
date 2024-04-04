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
