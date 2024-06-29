import asyncio
import time

import torch
from auto_gptq import exllama_set_max_input_length
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model = None
tokenizer = None


async def load_model():
    global model, tokenizer
    now = time.time()
    model_name_or_path = "TheBloke/Mistral-7B-Instruct-v0.2-GPTQ"
    # model_name_or_path = "TheBloke/deepseek-coder-6.7B-instruct-GPTQ"
    revision = "gptq-4bit-32g-actorder_True"
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        device_map="auto",
        trust_remote_code=False,
        revision=revision,
        cache_dir="./cache",
    )
    model = exllama_set_max_input_length(model, max_input_length=4096)
    print(f"Model loaded in {time.time() - now :.2f} seconds")
    # now = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)
    # print(f"Tokenizer loaded in {time.time() - now :.2f} seconds")


# def generate_text_stream(prompt, max_length=50):
#     inputs = tokenizer(prompt, return_tensors="pt")
#     inputs = inputs.to(model.device)
#     output_sequence = inputs["input_ids"]
#     model.eval()

#     with torch.no_grad():
#         for _ in range(max_length):
#             outputs = model(output_sequence)
#             next_token_logits = outputs.logits[:, -1, :]
#             next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
#             output_sequence = torch.cat([output_sequence, next_token], dim=-1)
#             yield tokenizer.decode(output_sequence[0])


# Generator function to yield data
async def generate_data(request_body, prompt):
    try:
        inputs = tokenizer.encode(prompt, return_tensors="pt")
        inputs = inputs.to(model.device)
        # outputs = model.generate(inputs, max_length=1024, do_sample=True)
        outputs = model.generate(
            inputs,
            max_length=request_body.max_new_tokens,
            do_sample=request_body.do_sample,
            temperature=request_body.temperature,
            top_p=request_body.top_p,
            top_k=request_body.top_k,
            repetition_penalty=request_body.repetition_penalty,
            num_beams=request_body.num_beams,
            num_return_sequences=request_body.num_return_sequences,
            no_repeat_ngram_size=request_body.no_repeat_ngram_size,
            length_penalty=request_body.length_penalty,
            early_stopping=request_body.early_stopping,
        )
        for output in outputs:
            generated_text = tokenizer.decode(output, skip_special_tokens=True)
            generated_text = generated_text.split("[/INST]")[1]
            yield generated_text + "\n"
            await asyncio.sleep(0.1)  # Adjust as needed
    except Exception as e:
        yield f"Error generating text: {e}\n"


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await load_model()


class GenerateTextRequest(BaseModel):
    prompt: str
    max_new_tokens: int
    do_sample: bool
    temperature: float
    top_p: float
    top_k: int
    repetition_penalty: float
    num_beams: int
    num_return_sequences: int
    no_repeat_ngram_size: int
    length_penalty: float = 1.0
    early_stopping: bool = False


# @app.post("/")
# async def generate_and_stream_text(request_body: GenerateTextRequest):
#     print(">>>", request_body.prompt)
#     if model is None or tokenizer is None:
#         raise HTTPException(status_code=503, detail="Model and tokenizer not loaded")

#     prompt_template = f"""<s>[INST] {request_body.prompt} [/INST]
# """

#     # Create a streaming response
#     # return StreamingResponse(generate_text_stream(prompt_template))

#     return StreamingResponse(
#         generate_data(request_body, prompt_template), media_type="text/plain"
#     )


@app.post("/")
async def generate_text(request_body: GenerateTextRequest):
    if not model or not tokenizer:
        raise HTTPException(status_code=503, detail="Model/Tokenizer not loaded")
    # now = time.time()
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=request_body.max_new_tokens,
        do_sample=request_body.do_sample,
        temperature=request_body.temperature,
        top_p=request_body.top_p,
        top_k=request_body.top_k,
        repetition_penalty=request_body.repetition_penalty,
        num_beams=request_body.num_beams,
        num_return_sequences=request_body.num_return_sequences,
        no_repeat_ngram_size=request_body.no_repeat_ngram_size,
        length_penalty=request_body.length_penalty,
        early_stopping=request_body.early_stopping,
    )
    # print(f"Pipeline loaded in {time.time() - now :.2f} seconds")
    try:
        prompt_template = f"""<s>[INST] {request_body.prompt} [/INST]
"""
        resp = pipe(prompt_template)[0]["generated_text"].split("[/INST]")[1]
        return {"generated_text": resp.strip()}
    except Exception as e:
        # print stacktrace
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# async def load_model():
#     global model, tokenizer
#     model_name_or_path = "TheBloke/Mistral-7B-Instruct-v0.2-GPTQ"
#     revision = "gptq-4bit-32g-actorder_True"
#     try:
#         now = time.time()
#         model = await asyncio.to_thread(
#             AutoModelForCausalLM.from_pretrained,
#             model_name_or_path,
#             revision=revision,
#             device_map="auto",
#             trust_remote_code=False,
#             cache_dir="./cache",
#         )
#         model = exllama_set_max_input_length(model, max_input_length=4096)
#         print(f"Model loaded in {time.time() - now:.2f} seconds")

#         now = time.time()
#         tokenizer = await asyncio.to_thread(
#             AutoTokenizer.from_pretrained, model_name_or_path, use_fast=True
#         )
#         print(f"Tokenizer loaded in {time.time() - now:.2f} seconds")
#     except Exception as e:
#         print(f"Error loading model or tokenizer: {e}")


# @app.on_event("startup")
# async def on_startup():
#     await load_model()
