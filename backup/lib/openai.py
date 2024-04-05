import os
from copy import deepcopy

from dotenv import load_dotenv
from ghost.utils.openai import OpenAIChatLLM
from openai import OpenAI
from pydantic import BaseModel, Field

ai = OpenAIChatLLM()
load_dotenv()


def ai_create_code(chat_history, sample_code):
    # resp = client.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": ,
    #         }
    #     ]
    #     + chat_history,
    #     model="gpt-4-0125-preview",
    #     response_format={"type": "json_object"},
    # )
    # resp = resp.choices[0].message.content
    # resp = json.loads(resp)
    # if resp.get("code"):
    #     raw_code = resp["code"]
    # else:
    #     raw_code = ""

    # if resp.get("file_location"):
    #     file_location = resp["file_location"]
    # else:
    #     file_location = "tmp.py"

    return code, file_location


def ai(system, chat_history):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    resp = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system},
        ]
        + chat_history,
        model="gpt-4-0125-preview",
    )
    return resp.choices[0].message.content
