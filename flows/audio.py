import asyncio

import httpx
from prefect import flow, task

from config import url


@task
async def example_task(description):
    await asyncio.sleep(5)
    return f"Task Result: {name} {description}"


@flow(name="Analyse Audio")
async def analyse_audio(name, description):
    task_result = await example_task(description)
    print(">>Result>>", task_result)

    return f"Task {name} created and executed successfully."
