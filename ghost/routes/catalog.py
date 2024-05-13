import asyncio
import json
import random
import re
from typing import List

import pandas as pd
import streamlit as st
from ghost.agents import ToolUserAgent
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


def create_dummy_catalog(num_products=1000):
    """
    Create a larger and more diverse dummy data set for an e-commerce catalog with randomly generated data,
    including detailed tags and cost calculations.

    Parameters:
    num_products (int): Number of products to generate.

    Returns:
    pd.DataFrame: A DataFrame with the generated product catalog.
    """

    # Defining possible attributes for products
    product_types = [
        "Jacket",
        "Boots",
        "Dress",
        "Scarf",
        "Sunglasses",
        "Coat",
        "Jeans",
        "T-Shirt",
        "Earrings",
        "Wristwatch",
        "Sneakers",
        "Sweater",
        "Gown",
        "Bag",
        "Scarf",
        "Tee",
        "Loafers",
        "Hat",
        "Necklace",
        "Blazer",
    ]
    materials = [
        "Denim",
        "Leather",
        "Floral",
        "Silk",
        "Polarized",
        "Classic",
        "Skinny",
        "Cotton",
        "Bohemian",
        "Canvas",
        "Woolen",
        "Velvet",
        "Cashmere",
        "Graphic",
        "Suede",
        "Knit",
        "Statement",
        "Tailored",
    ]
    colors = [
        "Blue",
        "Black",
        "Red",
        "Multicolor",
        "Grey",
        "Beige",
        "White",
        "Gold",
        "Brown",
        "Purple",
        "Silver",
    ]
    seasons = ["Winter", "Summer", "All"]
    genders = ["Men", "Women", "Unisex"]

    data = {
        "Product ID": [f"P{str(i).zfill(4)}" for i in range(1, num_products + 1)],
        "Name": [
            random.choice(materials) + " " + random.choice(product_types)
            for _ in range(num_products)
        ],
        "Gender": [random.choice(genders) for _ in range(num_products)],
        "Tags": [None] * num_products,  # Placeholder for tags
        "MRP": [random.randint(200, 3000) for _ in range(num_products)],
        "Cost": [None] * num_products,  # Placeholder for cost
        "Colour Family": [random.choice(colors) for _ in range(num_products)],
        "Season": [random.choice(seasons) for _ in range(num_products)],
    }

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Generating Tags and Cost
    for index, row in df.iterrows():
        # Creating detailed tags
        style_tags = [
            row["Name"].split()[0].lower(),
            "style",
            row["Season"].lower(),
            "fashion",
        ]
        additional_tags = f"{row['Colour Family'].lower()}, {row['Gender'].lower()}, {', '.join(random.sample(style_tags, 2))}"
        df.at[index, "Tags"] = f"{row['Name'].lower()}, {additional_tags}"

        # Setting cost as a random percentage of MRP
        df.at[index, "Cost"] = round(
            row["MRP"] * random.uniform(0.5, 0.9)
        )  # Cost is between 50% - 90% of MRP

    return df


def run_seq(funclist, prompt, messages):
    if not st.session_state.seq_id:
        st.session_state.seq_id = 1
    else:
        if st.session_state.seq_id < len(funclist):
            st.session_state.seq_id += 1
    return funclist[st.session_state.seq_id - 1](prompt, messages)


catalog = pd.read_csv("products.csv")
catalog = catalog[
    [
        "product_name",
        "price_bc",
        "is_new_product",
        "is_pinned",
        "is_best_seller",
        "is_active",
        "created_date",
        "modified_date",
        "like_count",
        "price",
        "price_str",
        "url",
        "image",
        "barcode",
        "skin_type",
        "product",
        "price_range",
    ]
]
wardhabot = OpenAIChatLLM()
asyncio.run(
    wardhabot.set_system_prompt(
        f"""You are an agent that helps the user to search for products for an skincare manufacturer - Wardha. Start the conversation by introducing yourself and what kind of service you provide. Do not offer any kind of general advice.

Follow this standard protocol:
Protocol: You need to guide them to the right product.
Do this by finding the answers to these questions one by one (one question in one response, Give suggestions on the product and skin type while asking the questions) -
What product do they want to buy?
What is their skin type?
Once you know the answers to all these questions, reply in the following json code block format with the details of the product:
```json
{{
"product": "moisturizer",
"skin_type": "Dry"
}}
```
These are the possible values for product and skin_type:
product: {catalog['product'].unique().tolist()}
skin_type: {catalog.skin_type.unique().tolist()}
```
"""
    )
)

summarizer = OpenAIChatLLM()
asyncio.run(
    summarizer.set_system_prompt(
        "The user will give you a json filtered from a catalog database. Convert this json into a sentence. Include all the product links available in md format. If the user sends an empty json, then respond with 'I am sorry, I did not find any product matching the criteria'."
    )
)


def search_catalog(prompt, messages):
    # catalog = create_dummy_catalog()

    # class TagResp(BaseModel):
    #     tags: List[str]

    def intro(prompt, messages):
        st.markdown("This is your product catalog:")
        st.dataframe(catalog)
        return "Search by Vibe: Eg: Show me a face cream for oily skin"

    def search(prompt, messages):
        resp = asyncio.run(wardhabot(prompt))
        codeblock = re.findall(r"```json(.*?)```", resp, re.DOTALL)
        if codeblock:
            query = json.loads(codeblock[0])
            query_string = " & ".join(
                [f"{key} == '{value}'" for key, value in query.items()]
            )
            filtered_df = catalog.query(query_string)

            # st.markdown(f"Filtered Products: {filtered_df}")
            # st.dataframe(filtered_df)
            resp = asyncio.run(summarizer(str(filtered_df.to_json())))
            return resp
            # return "Can I help you with anything else?"
        else:
            return resp
        # tool_user = ToolUserAgent(
        #     chatllm=OpenAIChatLLM(),
        #     tools=[
        #         PythonInterpreterTool(),
        #     ],
        # )
        # resp = asyncio.run(tool_user(prompt))
        # return resp
        # results = pd.DataFrame()
        # for tag in tags.tags:
        #     matched_items = catalog[catalog["Tags"].str.contains(tag, case=False)]
        #     results = pd.concat([results, matched_items]).drop_duplicates()
        # st.dataframe(results)
        # return results

    func_list = [intro, search]
    return run_seq(func_list, prompt, messages)
