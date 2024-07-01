from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from api.chat import router as chat_router
from api.task import router as task_router


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url} {request.query_params} ")
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response


app = FastAPI(title="Task Management API", version="1.0.0")
app.add_middleware(LogMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health():
    return {"status": "ok"}


app.include_router(chat_router)
app.include_router(task_router)
