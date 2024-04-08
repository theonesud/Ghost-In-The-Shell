# import asyncio
import os

import instructor
import tiktoken
from ghost import ChatLLM, Tokenizer
from openai import OpenAI

# from ghost.agents import ToolUserAgent
# from ghost.tools import PythonInterpreterTool, TerminalTool


# gpt-3.5-turbo-0125
# gpt-4-0125-preview
class OpenAITokenizer(Tokenizer):
    def __init__(self):
        super().__init__()

    async def _tokenize(self, text):
        return tiktoken.encoding_for_model("gpt-4-0125-preview").encode(text)


class OpenAIChatLLM(ChatLLM):
    def __init__(self):
        super().__init__(tokenizer=OpenAITokenizer())

    async def _reply(self, prompt, resp_model=None):
        if resp_model:
            openai = OpenAI()
            openai.api_key = os.environ["OPENAI_API_KEY"]
            self.client = instructor.from_openai(openai)
            resp = self.client.chat.completions.create(
                model="gpt-4-0125-preview",
                temperature=0.1,
                response_model=resp_model,
                messages=[
                    {"role": msg.role, "content": msg.content}
                    for msg in self.chat_history
                ],
            )
            return resp
        else:
            openai = OpenAI()
            openai.api_key = os.environ["OPENAI_API_KEY"]
            completion = openai.chat.completions.create(
                model="gpt-4-0125-preview",
                temperature=0.1,
                messages=[
                    {"role": msg.role, "content": msg.content}
                    for msg in self.chat_history
                ],
            )
            return completion.choices[0].message.content
