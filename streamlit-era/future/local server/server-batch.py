import asyncio
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()


# Define the request model
class TextRequest(BaseModel):
    prompt: str


# Initialize your model here (as per your existing setup)

# Queue for accumulating requests
request_queue = []
batch_size = 10  # Define your batch size
batch_process_interval = 5  # Time in seconds to wait before processing a batch


async def batch_processor():
    """
    Periodically process the requests in batches.
    """
    global request_queue
    while True:
        await asyncio.sleep(batch_process_interval)
        if request_queue:
            # Process the batch
            prompts = [req.prompt for req in request_queue]
            # Assuming 'pipe' is your model's pipeline
            responses = pipe(prompts)

            # Map responses back to requests and clear the queue
            for req, res in zip(request_queue, responses):
                req.response = res

            request_queue = []


# Start the batch processor in the background
@app.on_event("startup")
async def start_batch_processor():
    asyncio.create_task(batch_processor())


@app.post("/generate/", response_model=List[str])
async def generate_text(request: TextRequest):
    request.response = None
    request_queue.append(request)

    # Wait for the response to be filled
    while request.response is None:
        await asyncio.sleep(0.1)

    return request.response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# Explanation

#     Accumulation: Requests are stored in request_queue.
#     Batch Processing: The batch_processor function runs in the background and periodically checks request_queue. If there are any accumulated requests, it processes them in a batch.
#     Response Mapping: After processing, responses are mapped back to their corresponding requests.
#     Asynchronous Waiting: The endpoint generate_text adds the request to the queue and waits asynchronously for the response to be populated by the batch processor.

# Considerations

#     Timeouts: Implement a mechanism to handle timeouts. If the server gets overloaded, requests might wait indefinitely.
#     Error Handling: Add robust error handling, especially for mapping batch responses back to requests.
#     Scalability: Depending on the load, you might need to adjust the batch size and processing interval.
#     Concurrency: Ensure that your model pipeline (pipe) can handle batch inputs and is thread-safe if needed.
#     Request Ordering: This implementation does not guarantee the order of processing. If the order is important, you'll need additional logic to handle it.
