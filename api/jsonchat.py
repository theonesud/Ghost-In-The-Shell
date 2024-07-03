import asyncio
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel, Field

from config import jsonai
from model.io import ChatCompletionRequest, Message

router = APIRouter(prefix="/json")


class UserRequest(BaseModel):
    query: str


class LLMresp(BaseModel):
    content: str = Field(description="Response content")
    sentiment: str = Field(description="Sentiment of the response")


async def _resp_async_generator(
    messages: List[Message], model: str, max_tokens: int, temperature: float
):
    response = jsonai.chat.completions.create_partial(
        model=model,
        response_model=LLMresp,
        stream=True,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": m.role, "content": m.content} for m in messages],
    )
    # logger.info(f"Generated Response: {response}")
    for chunk in response:
        resp_json = chunk.model_dump_json()
        yield f"data: {resp_json} \n\n"
        await asyncio.sleep(0.01)
    yield "data: [DONE]"


@router.post("/chat/completions")
async def json_chat_completion(request: ChatCompletionRequest):
    try:
        logger.info(f"Request Params: {request}")
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
                airesp = jsonai.chat.completions.create(
                    model=request.model,
                    response_model=LLMresp,
                    messages=[
                        {"role": m.role, "content": m.content} for m in request.messages
                    ],
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                )
                return airesp
        else:
            return HTTPException(status_code=400, detail="No messages provided")
    except Exception as e:
        logger.exception(e)
        return HTTPException(status_code=500, detail=str(e))
