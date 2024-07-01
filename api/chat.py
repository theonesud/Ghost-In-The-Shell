import asyncio
import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from tinydb import Query, TinyDB

from config import openai
from model.db import create_new_chat, get_all_chats, get_chat, get_db, update_chat
from model.io import ChatCompletionRequest, Message

router = APIRouter(prefix="/v1")


async def _resp_async_generator(
    messages: List[Message], model: str, max_tokens: int, temperature: float
):
    chat_history = [{"role": m.role, "content": m.content} for m in messages]
    logger.info(f"Before generate: {chat_history}")
    response = openai.chat.completions.create(
        model=model,
        messages=chat_history,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True,
    )
    logger.info(f"After generate: {response}")

    for chunk in response:
        chunk_data = chunk.to_dict()
        yield f"data: {json.dumps(chunk_data)}\n\n"
        await asyncio.sleep(0.01)
    yield "data: [DONE]\n\n"


@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    try:
        logger.info(f"Received request: {request}")
        if request.messages:
            if request.stream:
                return StreamingResponse(
                    _resp_async_generator(
                        messages=request.messages,
                        model=request.model,
                        max_tokens=request.max_tokens,
                        temperature=request.temperature,
                    ),
                    media_type="application/x-ndjson",
                )
            else:
                response = openai.chat.completions.create(
                    model=request.model,
                    messages=[
                        {"role": m.role, "content": m.content} for m in request.messages
                    ],
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                )
                return response
        else:
            return HTTPException(status_code=400, detail="No messages provided")

    except Exception as e:
        logger.exception(f"Error generating response: {e}")
        return HTTPException(status_code=500, detail=str(e))


# @router.post("/generate_response/{chat_id}")
# async def generate_response(
#     chat_id: Optional[str], prompt: InputPrompt, db: TinyDB = Depends(get_db)
# ):
#     try:
#         if chat_id == "0":
#             chat_id, chat = await create_new_chat(db)
#         else:
#             chat = await get_chat(chat_id, db)
#         chat.append({"role": "user", "content": prompt.input_prompt})

#         logger.info(f"Generating response for chat {chat_id}")
#         resp_stream = generate(chat)

#         def generate_stream():
#             for chunk in resp_stream:
#                 llm_response = LLMResp.model_validate(chunk)
#                 package = llm_response.model_dump()
#                 package["chat_id"] = chat_id
#                 package = json.dumps(package)
#                 yield package + "\n"
#             chat.append({"role": "assistant", "content": chunk.content})
#             update_chat(chat_id, chat, db)

#         return StreamingResponse(
#             generate_stream(), media_type="application/stream+json"
#         )

#     except Exception as e:
#         logger.exception(f"Error generating response: {e}")
#         return HTTPException(status_code=500, detail=str(e))


# @router.get("/")
# async def get_chats(db: TinyDB = Depends(get_db)):
#     return get_all_chats(db)


# @router.get("/{chat_id}")
# async def get_one_chat(chat_id: str, db: TinyDB = Depends(get_db)):
#     return await get_chat(chat_id, db)
