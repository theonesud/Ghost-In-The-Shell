# import asyncio
import asyncio
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import instructor
import pandas as pd
import tiktoken
from dotenv import load_dotenv
from ghost import ChatLLM, Tokenizer
from ghost.agents import ToolUserAgent
from ghost.schema.message import Message, MessageRole
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
from openai import OpenAI
from selenium.webdriver.firefox.options import Options

load_dotenv()

# from ghost.agents import ToolUserAgent
# from ghost.tools import PythonInterpreterTool, TerminalTool


# gpt-3.5-turbo-0125
# gpt-4-0125-preview
class OpenAITokenizer(Tokenizer):
    def __init__(self):
        super().__init__()

    async def _tokenize(self, text):
        return tiktoken.encoding_for_model("gpt-3.5-turbo").encode(text)


class OpenAIChatLLM(ChatLLM):
    def __init__(self):
        super().__init__(tokenizer=OpenAITokenizer())

    async def _reply(self, prompt, resp_model=None, history=None):
        systemprompt = None
        if history:
            if len(self.chat_history):
                sys = self.chat_history.pop(0)
                if sys.role == MessageRole.system:
                    systemprompt = sys.content
            if systemprompt:
                self.chat_history = [Message(role="system", content=systemprompt)]
                self.chat_history.extend(
                    [
                        Message(role=item["role"], content=item["content"])
                        for item in history
                    ]
                )
            else:
                self.chat_history = [
                    Message(role=item["role"], content=item["content"])
                    for item in history
                ]
        if resp_model:
            openai = OpenAI(base_url=os.getenv("OPENAI_URL"))
            openai.api_key = os.environ["OPENAI_API_KEY"]
            self.client = instructor.from_openai(openai, mode=instructor.Mode.JSON)
            resp = self.client.chat.completions.create(
                model=os.getenv("MODEL"),
                temperature=0.1,
                response_model=resp_model,
                messages=[
                    {"role": msg.role, "content": msg.content}
                    for msg in self.chat_history
                ],
            )
            return resp
        else:
            openai = OpenAI(base_url=os.getenv("OPENAI_URL"))
            openai.api_key = os.environ["OPENAI_API_KEY"]
            completion = openai.chat.completions.create(
                model=os.getenv("MODEL"),
                temperature=0.1,
                messages=[
                    {"role": msg.role, "content": msg.content}
                    for msg in self.chat_history
                ],
            )
            return completion.choices[0].message.content


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
# translator1 = OpenAIChatLLM()
# asyncio.run(translator1.set_system_prompt("Translate this text to english"))
ecommerce_support_responder = OpenAIChatLLM()
asyncio.run(
    ecommerce_support_responder.set_system_prompt(
        """The user is trying to search for the right outfit. Collect the following information about the outfit by asking questions one by one:
1. what style does the outfit have? - give specific examples like: urban, casual, streetwear, athleasure, gymwear, housewear
2. what season would they want to wear it in?
3. what would be the price range?
4. what is the occasion?
5. what is the material of the outfit?
6. what is the color of the outfit?
7. what is the brand of the outfit?
8. what is the size of the outfit?
etc
"""
    )
)
support_intents = """
1. where is my order?
2. raise a complain about my order.
"""
support_intent_recognizer = OpenAIChatLLM()
asyncio.run(
    support_intent_recognizer.set_system_prompt(f"""Which of the following intents is the user trying to do? Only reply with the serial number:
{support_intents}
Only reply with the serial number.
""")
)
# translator2 = OpenAIChatLLM()
# asyncio.run(
#     translator2.set_system_prompt(
#         "Translate the response to the original qeustions language"
#     )
# )
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
omw = OpenAIChatLLM()
asyncio.run(
    omw.set_system_prompt(
        "The user will give you an order id. Your job is to tell the user that their order is on the way is expected to arrive in 3 days"
    )
)
# register_complaint = None
register_complaint = OpenAIChatLLM()
asyncio.run(
    register_complaint.set_system_prompt(
        "Act as a customer support representative for our ecommerce fashion brand. We sell clothes online. People will come to you with their complaints. Your job is to register the complaint on our platform. You have all the information about our company policies and terms of service. You can offer refunds for anything. Do not offer general advice."
    )
)


# Our customers will come to you with their complaint about a product they ordered. Your job is to tell the user that your complaint has been registered and will be acted upon soon. Offer a reasonable amount of refund if necessary. If they say yes, then tell them the refund will be sent to their account shortly. Be consice. Do not give the user other tips. You have all the information about our company policies and terms of service. You can offer refunds for anything.
