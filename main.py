import logging

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO)


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logging.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logging.info(f"Response status: {response.status_code}")
        return response


# Initialize FastAPI app
app = FastAPI(title="Task Management API", version="1.0.0")

# Include routers
from api.chat import router as chat_router
from api.task import router as task_router

app.include_router(chat_router)
app.include_router(task_router)

# Register middleware
app.add_middleware(LogMiddleware)


# Health check endpoint
@app.get("/")
async def health():
    return {"status": "ok"}
