import logging
import logging.config

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from api.chat import router as chat_router
from api.task import router as task_router
from logger import RouterLoggingMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)


# class LogMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         logging.info(f"Request: {request.method} {request.url}")
#         response = await call_next(request)
#         logging.info(f"Response status: {response.status_code}")
#         return response


app = FastAPI(title="Task Management API", version="1.0.0")
# app.add_middleware(LogMiddleware)

# app.add_middleware(RouterLoggingMiddleware, logger=logging.getLogger(__name__))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify the correct origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health():
    return {"status": "ok"}


app.include_router(chat_router)
app.include_router(task_router)
# app.mount("/ui", StaticFiles(directory="ui"), name="ui")
