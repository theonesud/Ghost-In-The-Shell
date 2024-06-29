from prefect import flow, task


@task
async def process_task(task_data: dict):
    await asyncio.sleep(5)
    return {"status": "completed"}


@flow
async def background_task(task_data: dict):
    result = await process_task(task_data)
    return result
