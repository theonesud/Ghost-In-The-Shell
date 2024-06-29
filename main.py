from fastapi import FastAPI
from tinydb import TinyDB

from api.chat import router as chat_router
from api.task import router as task_router

# from db_util import db_instance

app = FastAPI(title="Task Management API", version="1.0.0")

app.include_router(chat_router)
app.include_router(task_router)


@app.get("/")
async def health():
    return {"status": "ok"}


# @app.on_event("startup")
# async def startup_event():
# Initialize or load the database
# global db_instance
# db_instance = TinyDB("db.json")


# @app.on_event("shutdown")
# async def shutdown_event():
# Clean up the database if necessary
# pass
