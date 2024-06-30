import asyncio

import httpx
from prefect import flow, task

from config import url


@task
async def example_task(description):
    await asyncio.sleep(5)
    return f"Task Result: {name} {description}"


@flow(name="Call a Function")
async def call_a_function(name, description):
    task_result = await example_task(description)
    print(">>Result>>", task_result)

    return f"Task {name} created and executed successfully."


@flow(name="Call an API")
async def call_an_api(name, description):
    task_result = await example_task(description)
    print(">>Result>>", task_result)

    return f"Task {name} created and executed successfully."


@flow(name="Open Browser")
async def open_browser(name, description):
    task_result = await example_task(description)
    print(">>Result>>", task_result)

    return f"Task {name} created and executed successfully."


@flow(name="Use Terminal")
async def use_terminal(name, description):
    task_result = await example_task(description)
    print(">>Result>>", task_result)

    return f"Task {name} created and executed successfully."
