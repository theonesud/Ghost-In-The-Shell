import os

import instructor
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

load_dotenv()

url = os.getenv("URL")
model_name = os.getenv("MODEL")
openai = OpenAI()
jsonai = instructor.from_openai(OpenAI(), mode=instructor.Mode.JSON)
