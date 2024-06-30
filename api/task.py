import asyncio

import httpx
from fastapi import APIRouter, HTTPException
from loguru import logger
from prefect import flow, task
from pydantic import BaseModel

from config import url
from flows import task_handlers
from model.io import TaskDetails

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/create/")
async def create_task(task_details: TaskDetails):
    logger.info("Creating task: " + task_details.type)
    try:
        task_func = task_handlers.get(task_details.type)
        if task_func:
            task_result = await task_func(**task_details.params)
            if task_result is not None:
                await webhook_state_handler(task_details.type, "Completed")
            else:
                return {"message": "Task execution failed"}
        else:
            return {"message": "Invalid task type"}
    except Exception as e:
        logger.exception(f"Task creation failed: {e}")
        return HTTPException(status_code=500, detail=str(e))


async def webhook_state_handler(task_name, task_state):
    webhook_url = f"{url}/tasks/webhook/"
    data = {"task_name": task_name, "task_state": str(task_state)}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(webhook_url, json=data)
        except httpx.RequestError as e:
            print(f"Failed to send webhook: {e}")


@router.post("/webhook/")
async def receive_webhook(data: dict):
    logger.info(f"Received webhook data: {data}")
    return {"message": "Webhook received successfully", "data": data}
