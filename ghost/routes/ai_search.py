import ast
import asyncio
import multiprocessing as mp
import re
from contextlib import redirect_stdout
from io import StringIO
from typing import List

import astor
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from ghost.utils.openai import OpenAIChatLLM
from pydantic import BaseModel, Field

load_dotenv()


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


catalog_data = create_dummy_catalog()
sales_data = create_dummy_sales()
ai = OpenAIChatLLM()


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
        ecom_tagger = OpenAIChatLLM()
        asyncio.run(
            ecom_tagger.set_system_prompt(
                f"Create the ecommerce website search tags for the user query. You can choose from the tags mentioned in this db column {catalog_data["Tags"]}"
            )
        )

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
        query_writer = OpenAIChatLLM()
        asyncio.run(
            query_writer.set_system_prompt(
                f"You are an expert in writing Python code using Pandas to solve the user's needs. Reply only with the code, do not explain or add comments. Here's the df.head() \n {sales_data.head()}. Write a complete python script using pandas in a code block ```python\n#code\n``` to help the user with the following query. You can write the code assuming df is present. If you want to import some library, you can."
            )
        )
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
        explainer = OpenAIChatLLM()
        asyncio.run(
            explainer.set_system_prompt(
                """You are an expert in explaining Python code using Pandas to solve the user's needs."""
            )
        )
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
