import asyncio
import time
from uuid import uuid4

import httpx
import requests
from fastapi import APIRouter, FastAPI, HTTPException
from loguru import logger
from prefect import Flow, Task, flow, get_client, task
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


@router.post("/create/")
async def create_task(task_details: TaskDetails):
    @flow(name="Example Flow")
    async def create_prefect_task(name, description):
        @task
        async def example_task(description):
            await asyncio.sleep(5)
            return f"Task Result: {name} {description}"

        task_result = await example_task(description)
        print(">>Result>>", task_result)

        async def webhook_state_handler(task_name, task_state):
            webhook_url = "http://0.0.0.0:8000/tasks/webhook/"
            data = {"task_name": task_name, "task_state": str(task_state)}
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(webhook_url, json=data)
                except httpx.RequestError as e:
                    print(f"Failed to send webhook: {e}")

        if task_result:
            await webhook_state_handler(name, "Completed")
        return f"Task {name} created and executed successfully."

    asyncio.create_task(
        create_prefect_task(task_details.name, task_details.description)
    )
    return {"message": "Task creation initiated successfully"}


@router.post("/webhook/")
async def receive_webhook(data: dict):
    logger.info(f"Received webhook data: {data}")
    return {"message": "Webhook received successfully", "data": data}
