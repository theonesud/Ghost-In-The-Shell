import asyncio
from typing import List

import pandas as pd
import streamlit as st
from ghost.utils.openai import OpenAIChatLLM
from pydantic import BaseModel, Field


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


def run_seq(funclist, prompt, messages):
    print("<<<<<<<<<<<<", st.session_state.seq_id)
    if not st.session_state.seq_id:
        st.session_state.seq_id = 1
    else:
        st.session_state.seq_id += 1
    print(">>>>>>>>>>>>>>>>>", st.session_state.seq_id)
    return funclist[st.session_state.seq_id](prompt, messages)


def search_catalog(prompt, messages):
    catalog = create_dummy_catalog()

    class TagResp(BaseModel):
        tags: List[str]

    def intro(prompt, messages):
        st.markdown("This is your product catalog:")
        st.dataframe(catalog)
        return "Search by Vibe: Eg: Show me a beautiful dress to wear at a party"

    def search(prompt, messages):
        ai = OpenAIChatLLM()
        asyncio.run(
            ai.set_system_prompt(
                f"Create the ecommerce website search tags for the user query. You can choose from the tags mentioned in this db column {catalog['Tags']}"
            )
        )
        tags = asyncio.run(ai(prompt, TagResp, messages))
        st.markdown(f"Filtering tags: {tags}")
        results = pd.DataFrame()
        for tag in tags:
            matched_items = catalog[catalog["Tags"].str.contains(tag, case=False)]
            results = pd.concat([results, matched_items]).drop_duplicates()
        st.dataframe(results)
        return results

    func_list = [intro, search]
    return run_seq(func_list, prompt, messages)
