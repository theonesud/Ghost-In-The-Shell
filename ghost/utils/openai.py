# import asyncio
import os

import ghost.utils.openai as openai
import tiktoken
from ghost import ChatLLM, Tokenizer

# from ghost.agents import ToolUserAgent
# from ghost.tools import PythonInterpreterTool, TerminalTool


class OpenAITokenizer(Tokenizer):
    def __init__(self):
        super().__init__()

    async def _tokenize(self, text):
        return tiktoken.encoding_for_model("gpt-3.5-turbo").encode(text)


class OpenAIChatLLM(ChatLLM):
    def __init__(self):
        super().__init__(tokenizer=OpenAITokenizer())
        openai.api_key = os.environ["OPENAI_API_KEY"]

    async def _reply(self, prompt):
        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            temperature=0.1,
            messages=[
                {"role": msg.role, "content": msg.content} for msg in self.chat_history
            ],
        )
        return completion.choices[0].message.content


# if __name__ == "__main__":
#     tool_user_agent = ToolUserAgent(
#         chatllm=OpenAIChatLLM(), tools=[TerminalTool(), PythonInterpreterTool()]
#     )
#     resp = asyncio.run(tool_user_agent("Count the number of lines in main.py"))
