import asyncio
import random
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


def search_catalog(prompt, messages):
    catalog = create_dummy_catalog()

    # class TagResp(BaseModel):
    #     tags: List[str]

    def intro(prompt, messages):
        st.markdown("This is your product catalog:")
        st.dataframe(catalog)
        return "Search by Vibe: Eg: Show me a beautiful dress to wear at a party"

    def search(prompt, messages):
        ai = OpenAIChatLLM()
        asyncio.run(
            ai.set_system_prompt(
                f"write the correct pandas queries to show the products the user wants. assume pandas is available as pd and the dataframe is available as df. This is the output of df.head: {catalog.head()}"
            )
        )
        query = asyncio.run(ai(prompt))
        st.markdown(f"Query: {query}")
        tool_user = ToolUserAgent(
            chatllm=OpenAIChatLLM(),
            tools=[
                PythonInterpreterTool(),
            ],
        )
        resp = asyncio.run(tool_user(prompt))
        return resp.output
        # results = pd.DataFrame()
        # for tag in tags.tags:
        #     matched_items = catalog[catalog["Tags"].str.contains(tag, case=False)]
        #     results = pd.concat([results, matched_items]).drop_duplicates()
        # st.dataframe(results)
        # return results

    func_list = [intro, search]
    return run_seq(func_list, prompt, messages)
