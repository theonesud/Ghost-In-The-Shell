import ast
import asyncio
import hmac
import multiprocessing as mp
from contextlib import redirect_stdout
from io import StringIO

import astor
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def reply_to_intent_1():
    pass


def create_dummy_catalog():
    """
    Create dummy data for the e-commerce catalog.
    """
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
        ],
        "MRP": [1200, 2500, 1800, 400, 1500, 3000, 1000, 500, 600, 2000],
        "Cost": [700, 1500, 1100, 200, 900, 1800, 500, 250, 300, 1200],
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
        ],
    }
    data = pd.DataFrame(data)
    for index, row in data.iterrows():
        new_tag = f"{row['Name'].lower()}, {row['Gender'].lower()}, {row['Season'].lower()}, {row['Colour Family'].lower()}"
        data.at[index, "Tags"] += f", {new_tag}"
    return pd.DataFrame(data)


def create_dummy_sales():
    rows = [
        {
            "Date": "2023-01-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 77,
            "Returns": 19,
            "Stock on Hand": 79,
            "Sales Channel": "Wholesale",
            "Discount": 0.01,
            "Cost": 26,
        },
        {
            "Date": "2023-02-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 195,
            "Returns": 11,
            "Stock on Hand": 100,
            "Sales Channel": "Wholesale",
            "Discount": 0.1,
            "Cost": 11,
        },
        {
            "Date": "2023-03-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 157,
            "Returns": 20,
            "Stock on Hand": 72,
            "Sales Channel": "Wholesale",
            "Discount": 0.21,
            "Cost": 35,
        },
        {
            "Date": "2023-04-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 158,
            "Returns": 3,
            "Stock on Hand": 78,
            "Sales Channel": "Online",
            "Discount": 0.02,
            "Cost": 11,
        },
        {
            "Date": "2023-05-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 138,
            "Returns": 14,
            "Stock on Hand": 55,
            "Sales Channel": "Online",
            "Discount": 0.19,
            "Cost": 48,
        },
        {
            "Date": "2023-06-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 186,
            "Returns": 15,
            "Stock on Hand": 85,
            "Sales Channel": "Wholesale",
            "Discount": 0.25,
            "Cost": 32,
        },
        {
            "Date": "2023-07-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 195,
            "Returns": 6,
            "Stock on Hand": 28,
            "Sales Channel": "Retail",
            "Discount": 0.22,
            "Cost": 40,
        },
        {
            "Date": "2023-08-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 146,
            "Returns": 1,
            "Stock on Hand": 85,
            "Sales Channel": "Wholesale",
            "Discount": 0.29,
            "Cost": 19,
        },
        {
            "Date": "2023-09-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 96,
            "Returns": 18,
            "Stock on Hand": 85,
            "Sales Channel": "Wholesale",
            "Discount": 0.17,
            "Cost": 20,
        },
        {
            "Date": "2023-10-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 186,
            "Returns": 8,
            "Stock on Hand": 49,
            "Sales Channel": "Retail",
            "Discount": 0.24,
            "Cost": 28,
        },
        {
            "Date": "2023-11-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 53,
            "Returns": 11,
            "Stock on Hand": 33,
            "Sales Channel": "Online",
            "Discount": 0.26,
            "Cost": 29,
        },
        {
            "Date": "2023-12-01T04:55:17.955Z",
            "Product ID": "P001",
            "Sales": 103,
            "Returns": 3,
            "Stock on Hand": 29,
            "Sales Channel": "Wholesale",
            "Discount": 0.25,
            "Cost": 16,
        },
        {
            "Date": "2023-01-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 175,
            "Returns": 2,
            "Stock on Hand": 41,
            "Sales Channel": "Retail",
            "Discount": 0.18,
            "Cost": 47,
        },
        {
            "Date": "2023-02-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 187,
            "Returns": 19,
            "Stock on Hand": 68,
            "Sales Channel": "Online",
            "Discount": 0.21,
            "Cost": 27,
        },
        {
            "Date": "2023-03-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 148,
            "Returns": 2,
            "Stock on Hand": 35,
            "Sales Channel": "Online",
            "Discount": 0.29,
            "Cost": 33,
        },
        {
            "Date": "2023-04-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 72,
            "Returns": 0,
            "Stock on Hand": 45,
            "Sales Channel": "Online",
            "Discount": 0.14,
            "Cost": 30,
        },
        {
            "Date": "2023-05-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 181,
            "Returns": 1,
            "Stock on Hand": 74,
            "Sales Channel": "Online",
            "Discount": 0.28,
            "Cost": 11,
        },
        {
            "Date": "2023-06-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 102,
            "Returns": 15,
            "Stock on Hand": 94,
            "Sales Channel": "Online",
            "Discount": 0.13,
            "Cost": 20,
        },
        {
            "Date": "2023-07-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 91,
            "Returns": 10,
            "Stock on Hand": 90,
            "Sales Channel": "Online",
            "Discount": 0.27,
            "Cost": 38,
        },
        {
            "Date": "2023-08-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 118,
            "Returns": 19,
            "Stock on Hand": 83,
            "Sales Channel": "Online",
            "Discount": 0.2,
            "Cost": 48,
        },
        {
            "Date": "2023-09-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 50,
            "Returns": 5,
            "Stock on Hand": 76,
            "Sales Channel": "Online",
            "Discount": 0.2,
            "Cost": 32,
        },
        {
            "Date": "2023-10-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 157,
            "Returns": 4,
            "Stock on Hand": 48,
            "Sales Channel": "Retail",
            "Discount": 0.12,
            "Cost": 17,
        },
        {
            "Date": "2023-11-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 151,
            "Returns": 0,
            "Stock on Hand": 64,
            "Sales Channel": "Wholesale",
            "Discount": 0.26,
            "Cost": 49,
        },
        {
            "Date": "2023-12-01T04:55:17.957Z",
            "Product ID": "P002",
            "Sales": 193,
            "Returns": 6,
            "Stock on Hand": 75,
            "Sales Channel": "Wholesale",
            "Discount": 0.06,
            "Cost": 19,
        },
        {
            "Date": "2023-01-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 84,
            "Returns": 10,
            "Stock on Hand": 64,
            "Sales Channel": "Wholesale",
            "Discount": 0.05,
            "Cost": 44,
        },
        {
            "Date": "2023-02-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 96,
            "Returns": 14,
            "Stock on Hand": 70,
            "Sales Channel": "Wholesale",
            "Discount": 0.27,
            "Cost": 22,
        },
        {
            "Date": "2023-03-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 101,
            "Returns": 11,
            "Stock on Hand": 37,
            "Sales Channel": "Wholesale",
            "Discount": 0.02,
            "Cost": 47,
        },
        {
            "Date": "2023-04-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 190,
            "Returns": 3,
            "Stock on Hand": 92,
            "Sales Channel": "Online",
            "Discount": 0.14,
            "Cost": 45,
        },
        {
            "Date": "2023-05-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 124,
            "Returns": 20,
            "Stock on Hand": 78,
            "Sales Channel": "Wholesale",
            "Discount": 0.04,
            "Cost": 29,
        },
        {
            "Date": "2023-06-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 90,
            "Returns": 18,
            "Stock on Hand": 92,
            "Sales Channel": "Retail",
            "Discount": 0.11,
            "Cost": 30,
        },
        {
            "Date": "2023-07-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 89,
            "Returns": 10,
            "Stock on Hand": 95,
            "Sales Channel": "Retail",
            "Discount": 0.03,
            "Cost": 31,
        },
        {
            "Date": "2023-08-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 147,
            "Returns": 12,
            "Stock on Hand": 35,
            "Sales Channel": "Online",
            "Discount": 0.21,
            "Cost": 39,
        },
        {
            "Date": "2023-09-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 140,
            "Returns": 12,
            "Stock on Hand": 24,
            "Sales Channel": "Retail",
            "Discount": 0.25,
            "Cost": 32,
        },
        {
            "Date": "2023-10-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 195,
            "Returns": 16,
            "Stock on Hand": 58,
            "Sales Channel": "Online",
            "Discount": 0.08,
            "Cost": 23,
        },
        {
            "Date": "2023-11-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 88,
            "Returns": 5,
            "Stock on Hand": 33,
            "Sales Channel": "Online",
            "Discount": 0.05,
            "Cost": 37,
        },
        {
            "Date": "2023-12-01T04:55:17.958Z",
            "Product ID": "P003",
            "Sales": 80,
            "Returns": 8,
            "Stock on Hand": 97,
            "Sales Channel": "Retail",
            "Discount": 0.06,
            "Cost": 37,
        },
        {
            "Date": "2023-01-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 108,
            "Returns": 4,
            "Stock on Hand": 89,
            "Sales Channel": "Retail",
            "Discount": 0.2,
            "Cost": 44,
        },
        {
            "Date": "2023-02-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 143,
            "Returns": 12,
            "Stock on Hand": 97,
            "Sales Channel": "Wholesale",
            "Discount": 0.03,
            "Cost": 18,
        },
        {
            "Date": "2023-03-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 161,
            "Returns": 5,
            "Stock on Hand": 63,
            "Sales Channel": "Online",
            "Discount": 0.22,
            "Cost": 37,
        },
        {
            "Date": "2023-04-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 133,
            "Returns": 20,
            "Stock on Hand": 30,
            "Sales Channel": "Wholesale",
            "Discount": 0.0,
            "Cost": 18,
        },
        {
            "Date": "2023-05-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 177,
            "Returns": 8,
            "Stock on Hand": 28,
            "Sales Channel": "Retail",
            "Discount": 0.22,
            "Cost": 30,
        },
        {
            "Date": "2023-06-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 53,
            "Returns": 9,
            "Stock on Hand": 22,
            "Sales Channel": "Online",
            "Discount": 0.05,
            "Cost": 40,
        },
        {
            "Date": "2023-07-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 143,
            "Returns": 19,
            "Stock on Hand": 53,
            "Sales Channel": "Online",
            "Discount": 0.18,
            "Cost": 23,
        },
        {
            "Date": "2023-08-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 76,
            "Returns": 9,
            "Stock on Hand": 39,
            "Sales Channel": "Wholesale",
            "Discount": 0.12,
            "Cost": 20,
        },
        {
            "Date": "2023-09-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 144,
            "Returns": 7,
            "Stock on Hand": 87,
            "Sales Channel": "Online",
            "Discount": 0.03,
            "Cost": 19,
        },
        {
            "Date": "2023-10-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 149,
            "Returns": 19,
            "Stock on Hand": 67,
            "Sales Channel": "Retail",
            "Discount": 0.2,
            "Cost": 46,
        },
        {
            "Date": "2023-11-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 147,
            "Returns": 10,
            "Stock on Hand": 28,
            "Sales Channel": "Wholesale",
            "Discount": 0.24,
            "Cost": 28,
        },
        {
            "Date": "2023-12-01T04:55:17.959Z",
            "Product ID": "P004",
            "Sales": 65,
            "Returns": 20,
            "Stock on Hand": 49,
            "Sales Channel": "Online",
            "Discount": 0.25,
            "Cost": 10,
        },
        {
            "Date": "2023-01-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 158,
            "Returns": 18,
            "Stock on Hand": 53,
            "Sales Channel": "Wholesale",
            "Discount": 0.21,
            "Cost": 23,
        },
        {
            "Date": "2023-02-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 176,
            "Returns": 13,
            "Stock on Hand": 39,
            "Sales Channel": "Wholesale",
            "Discount": 0.03,
            "Cost": 12,
        },
        {
            "Date": "2023-03-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 185,
            "Returns": 4,
            "Stock on Hand": 95,
            "Sales Channel": "Wholesale",
            "Discount": 0.02,
            "Cost": 31,
        },
        {
            "Date": "2023-04-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 148,
            "Returns": 7,
            "Stock on Hand": 23,
            "Sales Channel": "Retail",
            "Discount": 0.29,
            "Cost": 50,
        },
        {
            "Date": "2023-05-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 65,
            "Returns": 16,
            "Stock on Hand": 52,
            "Sales Channel": "Online",
            "Discount": 0.14,
            "Cost": 50,
        },
        {
            "Date": "2023-06-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 192,
            "Returns": 3,
            "Stock on Hand": 56,
            "Sales Channel": "Retail",
            "Discount": 0.04,
            "Cost": 41,
        },
        {
            "Date": "2023-07-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 189,
            "Returns": 0,
            "Stock on Hand": 44,
            "Sales Channel": "Wholesale",
            "Discount": 0.19,
            "Cost": 39,
        },
        {
            "Date": "2023-08-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 85,
            "Returns": 17,
            "Stock on Hand": 73,
            "Sales Channel": "Retail",
            "Discount": 0.04,
            "Cost": 17,
        },
        {
            "Date": "2023-09-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 82,
            "Returns": 2,
            "Stock on Hand": 66,
            "Sales Channel": "Online",
            "Discount": 0.16,
            "Cost": 48,
        },
        {
            "Date": "2023-10-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 94,
            "Returns": 10,
            "Stock on Hand": 96,
            "Sales Channel": "Wholesale",
            "Discount": 0.29,
            "Cost": 38,
        },
        {
            "Date": "2023-11-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 54,
            "Returns": 14,
            "Stock on Hand": 41,
            "Sales Channel": "Wholesale",
            "Discount": 0.3,
            "Cost": 17,
        },
        {
            "Date": "2023-12-01T04:55:17.959Z",
            "Product ID": "P005",
            "Sales": 86,
            "Returns": 4,
            "Stock on Hand": 79,
            "Sales Channel": "Wholesale",
            "Discount": 0.1,
            "Cost": 26,
        },
    ]

    return pd.DataFrame(rows)


def generate_search_tags(query, catalog_data):
    """
    Use OpenAI's GPT-3.5 API to convert a natural language query into searchable tags.
    """
    # take from data[tags] column
    # print(catalog_data)
    unique_tags = catalog_data["Tags"]
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON.",
                },
                {
                    "role": "user",
                    "content": f"Create the ecommerce website search tags for this query: {query}. You can choose from the tags mentioned in this db column {unique_tags} Output in this format: key:'response' -> val:['tag1', 'tag2', 'tag3']",
                },
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in generating search tags: {str(e)}")
        return []


def search_catalog(tags, catalog):
    """
    Search the catalog using generated tags.
    """
    results = pd.DataFrame()
    for tag in tags:
        matched_items = catalog[catalog["Tags"].str.contains(tag, case=False)]
        results = pd.concat([results, matched_items]).drop_duplicates()
    return results


def generate_python_query(description, df, history):
    """
    Use OpenAI's LLM to generate a Python query based on the user's description.
    """
    try:
        client = OpenAI()
        messages = []
        messages += history
        messages += [
            {
                "role": "system",
                "content": "You are an expert in writing Python code using Pandas to solve the user's needs. Reply only with the code, do not explain or add comments",
            },
            {
                "role": "user",
                "content": f"Here's the df.head() \n {df.head()}. Write a python script to help the user with the following query: {description}",
            },
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            # model="gpt-4-1106-preview",
            temperature=0.1,
            # response_format={"type": "json_object"},
            messages=messages,
        )

        return (
            response.choices[0]
            .message.content.replace("```python ", "")
            .replace("```", "")
            .replace("python", "")
        )
    except Exception as e:
        return f"Error in generating query: {str(e)}"


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


def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
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


def explain(code, result):
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            # model="gpt-4-1106-preview",
            # temperature=0.5,
            # response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in explaining Python code using Pandas to solve the user's needs",
                },
                {
                    "role": "user",
                    "content": f"Here's the code: {code}. Here's the output: {result}. Explain the code in simple english in a line and communicate the output of the last line.",
                },
            ],
        )

        return (
            response.choices[0]
            .message.content.replace("```python ", "")
            .replace("```", "")
            .replace("python", "")
        )
        # return response.choices[0].text
    except Exception as e:
        return f"Error in generating explaination: {str(e)}"


def main():
    st.title("AI Search")

    # Create and display dummy catalog data
    catalog_data = create_dummy_catalog()
    st.write("Catalog:")
    st.dataframe(catalog_data)

    sales_data = create_dummy_sales()
    st.write("Sales:")
    st.dataframe(sales_data)

    query = st.text_input(
        "Search by Vibe", "Show me something fancy to wear at a party"
    )

    if st.button("Search"):
        with st.spinner("Processing your query..."):
            # Generate search tags from the query
            search_tags = generate_search_tags(query, catalog_data)
            st.write(f"Search Tags: {eval(search_tags)['response']}")

            search_results = search_catalog(
                (eval(search_tags)["response"]), catalog_data
            )
            st.write("", search_results)

    query = st.text_input(
        "Ask a business question", "What was my sales compared to returns last month?"
    )

    if st.button("Analyse"):
        with st.spinner("Writing Code..."):
            # Generate search tags from the query
            python_code = generate_python_query(query, sales_data, [])
            st.code(f"{python_code}")

            run_results = asyncio.run(run_python_code(python_code, {"df": sales_data}))
            explaination = explain(python_code, run_results)

            st.write("", explaination)


if __name__ == "__main__":
    # if not check_password():
    #     st.stop()
    main()
