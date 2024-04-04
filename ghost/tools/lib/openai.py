import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def ai_create_code(system_prompt, chat_history, sample_code):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    resp = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""{system_prompt}
Example Code:
```python
{sample_code}
```
Always respond as a json object like:"""
                + """{
    "file_location": "./filename.py"
    "code": ```python
    # your code here
    ```,
}
""",
            }
        ]
        + chat_history,
        model="gpt-4-0125-preview",
        response_format={"type": "json_object"},
    )
    resp = resp.choices[0].message.content
    resp = json.loads(resp)
    if resp.get("code"):
        raw_code = resp["code"]
    else:
        raw_code = ""

    if resp.get("file_location"):
        file_location = resp["file_location"]
    else:
        file_location = "tmp.py"

    code = raw_code.split("```python")[1].split("```")[0]
    if not code:
        code = raw_code.split("```")[1].split("```")[0]

    return code, file_location


def ai(system, chat_history):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    resp = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system},
        ] + chat_history,
        model="gpt-4-0125-preview",
    )
    return resp.choices[0].message.content
