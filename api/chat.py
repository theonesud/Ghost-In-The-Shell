import json
import os
import pprint
import time
import uuid
from typing import Optional

import instructor
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel, Field
from rich.console import Console
from tinydb import Query, TinyDB

from db_util import get_db

router = APIRouter(prefix="/chats", tags=["chats"])

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_URL")
model_name = os.getenv("MODEL")

openai = OpenAI(base_url=openai_base_url)
openai.api_key = openai_api_key
client = instructor.from_openai(openai, mode=instructor.Mode.JSON)

console = Console()


class InputPrompt(BaseModel):
    input_prompt: str


class Resp(BaseModel):
    content: str = Field(description="The content of the reply")
    sentiment: str = Field(description="The sentiment of the reply")


@router.get("/")
async def get_chats(db: TinyDB = Depends(get_db)):
    chats = db.table("chats").all()
    return chats


@router.get("/{chat_id}")
async def get_chat(chat_id: str, db: TinyDB = Depends(get_db)):
    Chat = Query()
    chat = db.table("chats").get(Chat.chat_id == chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.post("/generate_response/{chat_id}")
async def generate_response(
    chat_id: Optional[str], prompt: InputPrompt, db: TinyDB = Depends(get_db)
):
    Chat = Query()
    if not int(chat_id):
        chat_id = str(uuid.uuid4()).replace("-", "")
        chat_history = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]
        db.table("chats").insert(
            {
                "chat_id": chat_id,
                "messages": chat_history,
            }
        )
    else:
        chat = db.table("chats").get(Chat.chat_id == chat_id)
        chat_history = chat["messages"]

    chat_history.append({"role": "user", "content": prompt.input_prompt})

    PartialResp = instructor.Partial[Resp]
    resp = client.chat.completions.create(
        model=model_name,
        temperature=0.1,
        response_model=PartialResp,
        messages=chat_history,
        stream=True,
    )

    def generate_stream():
        for x in resp:
            package = {
                "content": x.content,
                "sentiment": x.sentiment,
                "chat_id": chat_id,
            }
            pprint.pprint(package)
            ai_resp = package.copy()
            package = json.dumps(package)
            yield package + "\n"
        chat_history.append(ai_resp)
        db.table("chats").update({"messages": chat_history}, Chat.chat_id == chat_id)

    return StreamingResponse(generate_stream(), media_type="application/stream+json")
