import ast
import asyncio
import multiprocessing as mp
import os
import random
import re
import urllib.parse
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import List

import astor
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from ghost.agents import ToolUserAgent
from ghost.schema.persona import Persona
from ghost.tools import (
    FileAppendTool,
    FileCopyTool,
    FileDeleteTool,
    FileFolderExistsTool,
    FileFolderMoveTool,
    FileReadTool,
    FileWriteTool,
    FolderCopyTool,
    FolderCreateTool,
    FolderDeleteTool,
    FolderListTool,
    FolderSearchTool,
    PythonInterpreterTool,
    TerminalTool,
)
from ghost.utils.openai import OpenAIChatLLM
from pydantic import BaseModel, Field
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

load_dotenv()


def create_dummy_catalog():
    """
    Create dummy data for the e-commerce catalog.
    """
    # Expanding the original database with more entries and details
    data = {
        "Product ID": [
            "P001",
            "P002",
            "P003",
            "P004",
            "P005",
            "P006",
            "P007",
            "P008",
            "P009",
            "P010",
            "P011",
            "P012",
            "P013",
            "P014",
            "P015",
            "P016",
            "P017",
            "P018",
            "P019",
            "P020",
        ],
        "Name": [
            "Vintage Denim Jacket",
            "Leather Ankle Boots",
            "Floral Print Maxi Dress",
            "Silk Scarf",
            "Polarized Aviator Sunglasses",
            "Classic Trench Coat",
            "Black Skinny Jeans",
            "White Cotton T-Shirt",
            "Bohemian Style Earrings",
            "Leather Wristwatch",
            "Canvas Sneakers",
            "Woolen Sweater",
            "Velvet Evening Gown",
            "Leather Messenger Bag",
            "Cashmere Scarf",
            "Graphic Tee",
            "Suede Loafers",
            "Chunky Knit Hat",
            "Statement Necklace",
            "Tailored Blazer",
        ],
        "Gender": [
            "Unisex",
            "Women",
            "Women",
            "Unisex",
            "Unisex",
            "Unisex",
            "Unisex",
            "Unisex",
            "Women",
            "Unisex",
            "Unisex",
            "Unisex",
            "Women",
            "Unisex",
            "Unisex",
            "Unisex",
            "Men",
            "Unisex",
            "Women",
            "Unisex",
        ],
        "Tags": [
            "jacket, denim, vintage, casual",
            "boots, leather, ankle, footwear",
            "dress, floral, maxi, summer",
            "scarf, silk, accessory, pattern",
            "sunglasses, aviator, polarized, fashion",
            "coat, trench, classic, outerwear",
            "jeans, skinny, black, denim",
            "t-shirt, cotton, white, basic",
            "earrings, bohemian, style, accessory",
            "wristwatch, leather, timeless, accessory",
            "sneakers, canvas, comfortable, casual",
            "sweater, woolen, warm, winter",
            "gown, velvet, evening, luxury",
            "bag, leather, messenger, utility",
            "scarf, cashmere, luxury, warmth",
            "tee, graphic, casual, cotton",
            "loafers, suede, comfortable, footwear",
            "hat, knit, chunky, warm",
            "necklace, statement, accessory, fashion",
            "blazer, tailored, formal, stylish",
        ],
        "MRP": [
            1200,
            2500,
            1800,
            400,
            1500,
            3000,
            1000,
            500,
            600,
            2000,
            800,
            900,
            3200,
            1800,
            1200,
            400,
            1100,
            300,
            700,
            2200,
        ],
        "Cost": [
            700,
            1500,
            1100,
            200,
            900,
            1800,
            500,
            250,
            300,
            1200,
            400,
            450,
            2000,
            900,
            600,
            200,
            550,
            150,
            350,
            1100,
        ],
        "Colour Family": [
            "Blue",
            "Black",
            "Red",
            "Multicolor",
            "Grey",
            "Beige",
            "Black",
            "White",
            "Gold",
            "Brown",
            "White",
            "Grey",
            "Purple",
            "Brown",
            "Red",
            "Black",
            "Brown",
            "Blue",
            "Silver",
            "Black",
        ],
        "Season": [
            "Winter",
            "All",
            "Summer",
            "All",
            "Summer",
            "Winter",
            "All",
            "Summer",
            "All",
            "All",
            "All",
            "Winter",
            "All",
            "All",
            "Winter",
            "Summer",
            "Summer",
            "Winter",
            "All",
            "All",
        ],
    }

    data = pd.DataFrame(data)
    for index, row in data.iterrows():
        new_tag = f"{row['Name'].lower()}, {row['Gender'].lower()}, {row['Season'].lower()}, {row['Colour Family'].lower()}"
        data.at[index, "Tags"] += f", {new_tag}"
    return pd.DataFrame(data)


def create_dummy_sales():
    rows = []
    product_ids = [
        "P001",
        "P002",
        "P003",
        "P004",
        "P005",
        "P006",
        "P007",
        "P008",
        "P009",
        "P010",
        "P011",
        "P012",
        "P013",
        "P014",
        "P015",
        "P016",
        "P017",
        "P018",
        "P019",
        "P020",
    ]
    sales_channels = ["Wholesale", "Retail", "Online"]
    discounts = [0.01, 0.05, 0.1, 0.15, 0.2]
    start_date = datetime(year=2023, month=1, day=1)

    for _ in range(100):  # Generating 100 sales entries
        date = start_date + timedelta(days=random.randint(0, 365))
        product_id = random.choice(product_ids)
        sales = random.randint(50, 200)
        returns = random.randint(5, 20)
        stock_on_hand = random.randint(50, 200)
        sales_channel = random.choice(sales_channels)
        discount = random.choice(discounts)
        cost = random.randint(10, 50)

        row = {
            "Date": date.isoformat() + "Z",
            "Product ID": product_id,
            "Sales": sales,
            "Returns": returns,
            "Stock on Hand": stock_on_hand,
            "Sales Channel": sales_channel,
            "Discount": discount,
            "Cost": cost,
        }
        rows.append(row)
    return pd.DataFrame(rows)


catalog_data = create_dummy_catalog()
sales_data = create_dummy_sales()
ecom_tagger = OpenAIChatLLM()
asyncio.run(
    ecom_tagger.set_system_prompt(
        f"Create the ecommerce website search tags for the user query. You can choose from the tags mentioned in this db column {catalog_data['Tags']}"
    )
)
query_writer = OpenAIChatLLM()
asyncio.run(
    query_writer.set_system_prompt(
        f"You are an expert in writing Python code using Pandas to solve the user's needs. Reply only with the code, do not explain or add comments. Here's the df.head() \n {sales_data.head()}. Write a complete python script using pandas in a code block ```python\n#code\n``` to help the user with the following query. You can write the code assuming df is present. If you want to import some library, you can."
    )
)
explainer = OpenAIChatLLM()
asyncio.run(
    explainer.set_system_prompt(
        """You are an expert in explaining Python code using Pandas to solve the user's needs."""
    )
)
persona = OpenAIChatLLM()
pather = OpenAIChatLLM()
asyncio.run(
    pather.set_system_prompt("""Reply with the following paths based on what the user wants to create/edit:
api/route.py - the CRUD routes for a resource
model/db.py - the sqlalchemy db models for a resource
model/ql.py - the pydantic models for CRUD endpoint body verification
scripts/run.sh - run the server locally
scripts/deploy.sh - deploy the server
scripts/test.sh - run pytest tests
tests/test_route.py - test the CRUD routes
tests/locustfile.py - test the server performance
Dockerfile - build the docker image
config.py - global variables and configs
main.py - the main server
requirements.txt - the python dependencies
pyproject.toml - the app info
""")
)
coder = OpenAIChatLLM()
asyncio.run(
    coder.set_system_prompt(
        """"Edit this template according to the user's needs. Follow the template closely and add all the features to it without the user specifying. Be very mindful of the usecase the user is trying to achieve."""
    )
)
with open(Path("ghost/sop/prd.md"), "r") as f:
    prd = f.read()
asker = OpenAIChatLLM()
asyncio.run(
    asker.set_system_prompt(f"""Your job is to create a set of questions for the user. From the answers of the questions you should be able to create a PRD like the one I've mentioned below. Ask very specific questions to the user. You should have details about the database structure, route structure, implementation details, any special requirements. Example PRD: {prd}
""")
)
prdmaster = OpenAIChatLLM()
asyncio.run(
    prdmaster.set_system_prompt(
        f"Create a PRD based on the given structure and the user's requirements. It should have details about the database structure, route structure, implementation details, any special requirements. Example PRD Structure: {prd}"
    )
)
tool_user = ToolUserAgent(
    chatllm=OpenAIChatLLM(),
    tools=[
        PythonInterpreterTool(),
        TerminalTool(),
        FileAppendTool(),
        FileCopyTool(),
        FileDeleteTool(),
        FileFolderExistsTool(),
        FileFolderMoveTool(),
        FileReadTool(),
        FileWriteTool(),
        FolderCopyTool(),
        FolderCreateTool(),
        FolderDeleteTool(),
        FolderListTool(),
        FolderSearchTool(),
        PythonInterpreterTool(),
        TerminalTool(),
    ],
)
translator1 = OpenAIChatLLM()
asyncio.run(translator1.set_system_prompt("Translate this text to english"))
responder = OpenAIChatLLM()
asyncio.run(responder.set_system_prompt("Respond to the users query normally"))
translator2 = OpenAIChatLLM()
asyncio.run(
    translator2.set_system_prompt(
        "Translate the response to the original qeustions language"
    )
)
emailer = OpenAIChatLLM()
asyncio.run(
    emailer.set_system_prompt(
        "Create a personalized email for the user mentioned customer segment"
    )
)
tweeter = OpenAIChatLLM()
asyncio.run(
    tweeter.set_system_prompt(
        "Generate an engaging twitter post based on the user's usecase. Do not use hashtags. The post should be relavent to the user's query and provide great value"
    )
)
options = Options()
options.headless = True
downloader = OpenAIChatLLM()
asyncio.run(
    downloader.set_system_prompt(
        "Create valid urls from the users query Eg: https://www.google.com, https://www.facebook.com"
    )
)


class TagResp(BaseModel):
    tags: List[str]


def reply_to_intent_1(prompt, messages):
    st.write("Catalog:")
    st.dataframe(catalog_data)
    if st.session_state.pair_index == 0:
        # st.write("Sales:")
        # st.dataframe(sales_data)
        st.session_state.pair_index = 1
        return "Search by Vibe: Eg: Show me a beautiful dress to wear at a party"
    elif st.session_state.pair_index == 1:
        tags = asyncio.run(ecom_tagger(prompt, TagResp))
        return search_catalog(tags.tags, catalog_data)


class PythonCode(BaseModel):
    code: str = Field(description="Python code in the format ````python\ncode\n```")


def reply_to_intent_2(prompt, messages):
    st.write("Sales:")
    st.dataframe(sales_data)
    if st.session_state.pair_index == 0:
        # st.write("Catalog:")
        # st.dataframe(catalog_data)
        st.session_state.pair_index = 1
        return "Ask a business question: Eg: What was my sales compared to returns last month?"
    elif st.session_state.pair_index == 1:
        resp = asyncio.run(
            query_writer(
                prompt,
                PythonCode,
            )
        )
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


class CodeResp(BaseModel):
    file_location: str = Field(
        description="File location based on the template location"
    )
    code: str = Field(
        description="Python code inside a codeblock like ```python\n# code here\n```"
    )


class PathResp(BaseModel):
    path: str = Field(description="Path to the file based on the template location")


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
        resp = asyncio.run(prdmaster(prompt))
        with open(Path("output/prd.md"), "w") as f:
            f.write(resp)
        return resp


def reply_to_intent_9(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return """I have access to tools to create, delete, copy, move, search, list and read files and folders.I can run python and shell code"""
    elif st.session_state.pair_index == 1:
        resp = asyncio.run(tool_user(prompt))
        return resp.output


def reply_to_intent_5(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Enter Customer Query (Non-English) Example: ¿Cuándo llegará mi pedido?"
    elif st.session_state.pair_index == 1:
        translation = asyncio.run(translator1(prompt))
        st.write(translation)
        response = asyncio.run(responder(translation))
        st.write(response)
        translation = asyncio.run(
            translator2(f"Response: {response}. Original question: {prompt}")
        )
        return translation


def reply_to_intent_6(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Enter Customer Segment"
    elif st.session_state.pair_index == 1:
        translation = asyncio.run(emailer(prompt))
        return translation


def reply_to_intent_7(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Enter Topic"
    elif st.session_state.pair_index == 1:
        translation = asyncio.run(tweeter(prompt))
        return translation


class URLList(BaseModel):
    urls: List[str] = []


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
        meta = asyncio.run(persona(prompt))
        return meta
