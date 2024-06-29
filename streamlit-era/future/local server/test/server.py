# File: server.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()


@app.get("/")
async def stream_words():
    async def generate():
        for word in ["Hello", "world", "this", "is", "a", "stream", "test"]:
            yield word + " "
            await asyncio.sleep(0.5)  # Introduce a delay to simulate streaming

    return StreamingResponse(generate(), media_type="text/plain")
