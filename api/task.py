from fastapi import APIRouter, HTTPException
from tinydb import TinyDB, Query
from model.db import get_db
from uuid import uuid4
from prefect import flow, task
from prefect.deployments import Deployment
import asyncio

router = APIRouter(prefix="/tasks", tags=["tasks"])

db = get_db()


@task
async def process_task(task_data: dict):
    await asyncio.sleep(5)
    return {"status": "completed"}


@flow
async def background_task(task_data: dict):
    result = await process_task(task_data)
    Task = Query()
    db.table("tasks").update(result, Task.task_id == task_data["task_id"])
    return result


@router.post("/")
async def create_task(task_data: dict):
    task_id = str(uuid4())
    task_data["task_id"] = task_id
    task_data["status"] = "pending"
    db.table("tasks").insert(task_data)

    deployment = Deployment.build_from_flow(
        flow=background_task,
        name=f"background_task_{task_id}",
        parameters={"task_data": task_data},
    )
    deployment.apply()

    return {"task_id": task_id}


@router.get("/")
async def get_tasks():
    tasks = db.table("tasks").all()
    return tasks


@router.post("/reprioritize")
async def reprioritize_task_queue(task_queue: list):
    # Implement task reprioritization logic here
    # For now, we'll return the updated queue
    return {"task_queue": task_queue}