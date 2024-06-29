import asyncio
import time
from uuid import uuid4

import requests
from fastapi import APIRouter, FastAPI, HTTPException
from prefect import Flow, Task, flow, task
from prefect.deployments import Deployment
from prefect.server.schemas.states import State
from pydantic import BaseModel
from tinydb import Query, TinyDB

from model.db import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])

db = get_db()


class TaskDetails(BaseModel):
    name: str
    description: str


# Define the state handler function
async def webhook_state_handler(task_name, task_state):
    webhook_url = "http://localhost:8000/tasks/webhook/"
    data = {"task_name": task_name, "task_state": str(task_state)}
    try:
        await requests.post(webhook_url, json=data)
    except requests.RequestException as e:
        print(f"Failed to send webhook: {e}")


# Define a Prefect task
@task
def example_task(description):
    print(description)
    time.sleep(5)
    return f"Task executed with description: {description}"


# Define a Prefect flow
@flow(name="Example Flow")
def create_prefect_task(name, description):
    task_result = example_task(description)
    print(">>>>", task_result)
    if task_result is not None:
        webhook_state_handler(name, "Completed")
    return f"Task {name} created and executed successfully."


@router.post("/create/")
async def create_task(task_details: TaskDetails):
    return create_prefect_task(task_details.name, task_details.description)


@router.post("/webhook/")
async def receive_webhook(data: dict):
    print(f"Received webhook data: {data}")
    return {"message": "Webhook received successfully", "data": data}


# @task
# async def process_task(task_data: dict):
#     await asyncio.sleep(5)
#     return {"status": "completed"}


# @flow
# async def background_task(task_data: dict):
#     result = await process_task(task_data)
#     Task = Query()
#     db.table("tasks").update(result, Task.task_id == task_data["task_id"])
#     return result


# @router.post("/")
# async def create_task(task_data: dict):
#     task_id = str(uuid4())
#     task_data["task_id"] = task_id
#     task_data["status"] = "pending"
#     db.table("tasks").insert(task_data)

#     deployment = Deployment.build_from_flow(
#         flow=background_task,
#         name=f"background_task_{task_id}",
#         parameters={"task_data": task_data},
#     )
#     deployment.apply()

#     return {"task_id": task_id}


# @router.get("/")
# async def get_tasks():
#     tasks = db.table("tasks").all()
#     return tasks


# @router.post("/reprioritize")
# async def reprioritize_task_queue(task_queue: list):
#     # Implement task reprioritization logic here
#     # For now, we'll return the updated queue
#     return {"task_queue": task_queue}
