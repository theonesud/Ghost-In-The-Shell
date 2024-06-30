import uuid

from fastapi import Depends, HTTPException
from tinydb import Query, TinyDB


def get_db():
    return TinyDB("db.json")


async def create_new_chat(db: TinyDB = Depends(get_db)):
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
    return chat_id, chat_history


async def get_chat(chat_id, db: TinyDB = Depends(get_db)) -> list[dict]:
    Chat = Query()
    chat = db.table("chats").get(Chat.chat_id == chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat["messages"]


def update_chat(chat_id, chat_history, db: TinyDB = Depends(get_db)):
    Chat = Query()
    db.table("chats").update({"messages": chat_history}, Chat.chat_id == chat_id)


def get_all_chats(db: TinyDB = Depends(get_db)):
    return db.table("chats").all()
