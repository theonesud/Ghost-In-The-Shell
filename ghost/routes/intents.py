import ast
import asyncio
import multiprocessing as mp
import os
import re
import urllib.parse
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import astor

# from google.cloud import translate_v2 as translate
import boto3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from ghost.schema.intents import (
    CodeResp,
    PathResp,
    PythonCode,
    TagResp,
    URLList,
)
from ghost.schema.persona import Persona
from ghost.utils.openai import (
    asker,
    catalog_data,
    coder,
    downloader,
    ecom_tagger,
    emailer,
    explainer,
    options,
    pather,
    persona,
    prdmaster,
    query_writer,
    responder,
    sales_data,
    tool_user,
    translator1,
    translator2,
    tweeter,
)
from rapidfuzz import fuzz, process
from selenium import webdriver

# translate_client = translate.Client()
lang = None
load_dotenv()

intents = """
1. search shopify catalog - uses chat based search to find the product in the catalog
2. talk to a business analyst - runs analysis on your sales data to answer any business questions
3. talk to a developer to create a python fastapi server
4. talk to the engineering manager to create a prd for backend team
5. talk to a regional customer support representative
6. talk to an email writer
7. talk to a twitter post writer
8. download given urls
9. access files/folders, run python and shell code
10. talk to one of many personas
"""


def reply_to_intent_1(prompt, messages):
    st.write("Catalog:")
    st.dataframe(catalog_data)
    if st.session_state.pair_index == 0:
        # st.write("Sales:")
        # st.dataframe(sales_data)
        st.session_state.pair_index = 1
        return "Search by Vibe: Eg: Show me a beautiful dress to wear at a party"
    elif st.session_state.pair_index == 1:
        tags = asyncio.run(ecom_tagger(prompt, TagResp, messages))
        return search_catalog(tags.tags, catalog_data)


def reply_to_intent_2(prompt, messages):
    st.write("Sales:")
    st.dataframe(sales_data)
    if st.session_state.pair_index == 0:
        # st.write("Catalog:")
        # st.dataframe(catalog_data)
        st.session_state.pair_index = 1
        return "Ask a business question: Eg: What was my sales compared to returns last month?"
    elif st.session_state.pair_index == 1:
        resp = asyncio.run(query_writer(prompt, PythonCode, messages))
        content = resp.code
        python_code = re.findall(r"```python(.*?)```", content, re.DOTALL)
        if not python_code:
            python_code = content
        # st.code(f"{python_code}")
        run_results = asyncio.run(run_python_code(python_code, {"df": sales_data}))

        explaination = asyncio.run(
            explainer(
                f"Here's the code: {python_code}. Here's the output: {run_results}. Explain the code in simple english in a line and communicate the output of the last line."
            )
        )
        # st.write("", explaination)
        return f"# Code:\n ```python{python_code}\n``` \n\n # Results: \n{run_results} \n # Explaination: \n{explaination}"


def search_catalog(tags, catalog):
    """
    Search the catalog using generated tags.
    """
    results = pd.DataFrame()
    for tag in tags:
        matched_items = catalog[catalog["Tags"].str.contains(tag, case=False)]
        results = pd.concat([results, matched_items]).drop_duplicates()
    st.dataframe(results)
    return results


def _target_func(queue, code: str, vars: dict) -> None:
    """Target function for the multiprocessing process.

    Imports are parsed separately and added to the global variables.

    The code is split into two parts:
    the first part is everything except the last statement.
    The first part is run using `exec()`.
    The last statement is run using `eval()` and the result is returned.
    If the `eval()` returns an error, the tool will return the error message with exit code 1.
    """
    try:
        global_vars = {"__builtins__": __builtins__}
        local_vars = vars
        tree = ast.parse(code)

        imports = [x for x in tree.body if isinstance(x, ast.Import)]
        imports_from = [x for x in tree.body if isinstance(x, ast.ImportFrom)]
        for import_ in imports:
            global_vars.update(
                {import_.names[0].name: __import__(import_.names[0].name)}
            )
        for import_from in imports_from:
            for name in import_from.names:
                global_vars.update(
                    {name.name: getattr(__import__(import_from.module), name.name)}
                )

        module = ast.Module(tree.body[:-1], type_ignores=[])
        exec(astor.to_source(module), global_vars, local_vars)

        module_end = ast.Module(tree.body[-1:], type_ignores=[])
        module_end_str = astor.to_source(module_end)
        io_buffer = StringIO()
        try:
            with redirect_stdout(io_buffer):
                ret = eval(module_end_str, global_vars, local_vars)
                if ret is None:
                    output = io_buffer.getvalue()
                else:
                    output = ret
        except Exception:
            with redirect_stdout(io_buffer):
                exec(module_end_str, global_vars, local_vars)
            output = io_buffer.getvalue()
        queue.put([output, 0])
    except Exception as e:
        queue.put([str(e), 1])


async def run_python_code(code: str, vars: dict = None, timeout=60):
    # print(code, vars)
    if not vars:
        vars = {}
    loop = asyncio.get_running_loop()
    queue = mp.Queue()
    process = mp.Process(target=_target_func, args=(queue, code, vars))
    process.start()
    process.join(timeout)
    if process.is_alive():
        process.kill()
        raise asyncio.TimeoutError
    result = await loop.run_in_executor(None, queue.get)
    return result[0]


def reply_to_intent_3(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Give a filename and a the contents of the file. Eg: Create a sqlalchemy db file for products, offers, inventory, and orders"
    elif st.session_state.pair_index == 1:
        resp = asyncio.run(pather(prompt, PathResp))
        with open(Path(f"ghost/sop/py/{resp.path}")) as f:
            code = f.read()

        resp = asyncio.run(
            coder(
                f"""
Example Code:
```python
{code}
```
Prompt: {prompt}""",
                CodeResp,
                messages,
            )
        )
        generated_code = resp.code
        file_location = resp.file_location
        generated_code = generated_code.lstrip("```python")
        generated_code = generated_code.lstrip("```")
        generated_code = generated_code.rstrip("```")
        # code = generated_code.split("```python")[1].split("```")[0]
        # if not code:
        #     code = generated_code.split("```")[1].split("```")[0]
        os.makedirs("output", exist_ok=True)
        file_location_path = Path(file_location)
        generated_loc = Path("output") / file_location_path
        generated_loc.parent.mkdir(parents=True, exist_ok=True)
        with open(generated_loc, "w") as f:
            f.write(generated_code)
        return f"```python\n{generated_code}\n```"


def reply_to_intent_4(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1

        resp = asyncio.run(asker(prompt))
        return resp

    elif st.session_state.pair_index == 1:
        resp = asyncio.run(prdmaster(prompt, history=messages))
        with open(Path("output/prd.md"), "w") as f:
            f.write(resp)
        return resp


# def translate_text(target: str, text: str) -> dict:
#     """Translates text into the target language.

#     Target must be an ISO 639-1 language code.
#     See https://g.co/cloud/translate/v2/translate-reference#supported_languages
#     """
#     if isinstance(text, bytes):
#         text = text.decode("utf-8")

#     result = translate_client.translate(text, target_language=target)

#     print("Text: {}".format(result["input"]))
#     print("Translation: {}".format(result["translatedText"]))
#     print("Detected source language: {}".format(result["detectedSourceLanguage"]))

#     return result


def translate_text(text, source_lang, target_lang):
    client = boto3.client(
        "translate",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )
    response = client.translate_text(
        Text=text, SourceLanguageCode=source_lang, TargetLanguageCode=target_lang
    )
    return response["TranslatedText"]


def reply_to_intent_5(prompt, messages):
    global lang
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Choose a language - Urdu, Gujarati, Latvian"
    elif st.session_state.pair_index == 1:
        st.session_state.pair_index = 2
        lang = process.extractOne(
            prompt, ["Urdu", "Gujarati", "Latvian"], scorer=fuzz.ratio
        )
        _map = {"Urdu": "ur", "Gujarati": "gu", "Latvian": "lv"}
        lang = _map[lang[0]]
        if lang == "ur":
            return "میں آپ کی کیسے مدد کر سکتا ہوں"
            return "Mein aapki kaise madat kar sakta hu?"
        elif lang == "gu":
            return "હું આપની શું મદદ કરી શકું"
            return "Huṁ āpanī śuṁ madad karī śakuṁ?"
        elif lang == "lv":
            return "kā es varu Jums palīdzēt?"
    elif st.session_state.pair_index == 2:
        translation = translate_text(lang, prompt)
        # translation = asyncio.run(translator1(prompt, history=messages))
        st.write(translation)
        response = asyncio.run(responder(translation, history=messages))
        st.write(response)
        translation = asyncio.run(
            translator2(
                f"Response: {response}. Original question: {prompt}", history=messages
            )
        )
        return translation


def reply_to_intent_6(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Enter Customer Segment"
    elif st.session_state.pair_index == 1:
        translation = asyncio.run(emailer(prompt, history=messages))
        return translation


def reply_to_intent_7(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Enter Topic"
    elif st.session_state.pair_index == 1:
        translation = asyncio.run(tweeter(prompt, history=messages))
        return translation


def reply_to_intent_8(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Which urls would you like to download?"
    elif st.session_state.pair_index == 1:
        urls = asyncio.run(downloader(prompt, URLList))
        driver = webdriver.Firefox(options=options)
        for url in urls.urls:
            driver.get(url)
            path = urllib.parse.urlparse(url).path.rstrip("/")
            path = path[1:]
            if not path:
                path = "index"
            filename = path.replace("/", "-") + ".html"
            print(filename)
            os.makedirs("output/downloads", exist_ok=True)
            with open("output/downloads/" + filename, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        return urls


def reply_to_intent_9(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return """I have access to tools to create, delete, copy, move, search, list and read files and folders.I can run python and shell code"""
    elif st.session_state.pair_index == 1:
        resp = asyncio.run(tool_user(prompt, history=messages))
        return resp.output


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
        meta = asyncio.run(persona(prompt, history=messages))
        return meta
