import asyncio

import httpx
from prefect import flow, task

from config import url


@task
async def example_task(name, description):
    await asyncio.sleep(5)
    return f"Task Result: {name} {description}"


@flow(name="Generate Image")
async def generate_image(name, description):
    task_result = await example_task(name, description)
    print(">>Result>>", task_result)

    return f"Task {name} created and executed successfully."


@flow(name="Understand Image")
async def understand_image(name, description):
    task_result = await example_task(name, description)
    print(">>Result>>", task_result)

    return f"Task {name} created and executed successfully."
