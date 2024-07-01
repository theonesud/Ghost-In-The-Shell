import os

import instructor
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

url = os.getenv("URL")
model_name = os.getenv("MODEL")
openai = OpenAI()
# llm = instructor.from_openai(openai, mode=instructor.Mode.JSON)
# llm = openai
