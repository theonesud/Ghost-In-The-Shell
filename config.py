import os

import instructor
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

url = os.getenv("URL")
# openai_api_key = os.getenv("OPENAI_API_KEY")
# openai_base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("MODEL")
openai = OpenAI()
# openai = OpenAI()
# openai.api_key = openai_api_key
# llm = instructor.from_openai(openai, mode=instructor.Mode.JSON)
# llm = openai
