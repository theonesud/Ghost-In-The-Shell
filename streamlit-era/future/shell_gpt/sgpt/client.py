import json
from pathlib import Path
from typing import Dict, Generator, List

import requests

from .cache import Cache
from .config import cfg

CACHE_LENGTH = int(cfg.get("CACHE_LENGTH"))
CACHE_PATH = Path(cfg.get("CACHE_PATH"))
REQUEST_TIMEOUT = int(cfg.get("REQUEST_TIMEOUT"))
DISABLE_STREAMING = str(cfg.get("DISABLE_STREAMING"))


class OpenAIClient:
    cache = Cache(CACHE_LENGTH, CACHE_PATH)

    def __init__(self, api_host: str, api_key: str) -> None:
        self.__api_key = api_key
        self.api_host = api_host

    @cache
    def _request(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 1,
        top_probability: float = 1,
    ) -> Generator[str, None, None]:
        """
        Make request to OpenAI API, read more:
        https://platform.openai.com/docs/api-reference/chat

        :param messages: List of messages {"role": user or assistant, "content": message_string}
        :param model: String gpt-3.5-turbo or gpt-3.5-turbo-0301
        :param temperature: Float in 0.0 - 2.0 range.
        :param top_probability: Float in 0.0 - 1.0 range.
        :return: Response body JSON.
        """
        stream = DISABLE_STREAMING == "false"
        data = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "top_p": top_probability,
            "stream": stream,
        }
        prompt = ""
        for message in messages:
            prompt += f"{message['role']}: {message['content']}\n"
        # endpoint = f"{self.api_host}/v1/chat/completions"
        # response = requests.post(
        #     endpoint,
        #     # Hide API key from Rich traceback.
        #     headers={
        #         "Content-Type": "application/json",
        #         "Authorization": f"Bearer {self.__api_key}",
        #     },
        #     json=data,
        #     timeout=REQUEST_TIMEOUT,
        #     stream=stream,
        # )

        def call_model(prompt):
            balanced_chat_mode = {
                "prompt": prompt,
                "max_new_tokens": 2048,
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.85,
                "top_k": 50,
                "repetition_penalty": 1.1,
                "num_beams": 1,
                "num_return_sequences": 1,
                "no_repeat_ngram_size": 2,
            }
            with requests.Session() as session:
                response = session.post(
                    "http://localhost:8000/", json=balanced_chat_mode, stream=True
                )
            assert response.status_code == 200
            # assert "generated_text" in response.json()
            return response
            # return response.json()["generated_text"]

        # def stream_response(prompt, stream=True):
        # print(">>>>prompt>>>>>>>", prompt)
        # response = ""
        response = call_model(prompt=prompt)

        # buffer = ""
        # for chunk in response.iter_content(chunk_size=1):  # Process one byte at a time
        #     print("<<<<", chunk.decode())
        # yield chunk.decode()
        # if chunk.endswith(
        #     b" "
        # ):  # If the byte is a space, we assume it's the end of a word
        #     buffer += chunk.decode()
        #     yield buffer
        #     buffer = ""
        # else:
        #     buffer += chunk.decode()

        # # response.raise_for_status()
        # # TODO: Optimise.
        # # https://github.com/openai/openai-python/blob/237448dc072a2c062698da3f9f512fae38300c1c/openai/api_requestor.py#L98
        if not stream:
            data = response.json()
            # yield data["choices"][0]["message"]["content"]  # type: ignore
            yield data["generated_text"]
            return

        for line in response.iter_lines():
            if line:  # checking if line is not empty
                decoded_line = line.decode("utf-8")
                words = decoded_line.split()
                for word in words:
                    yield word + " "  # Yield each word followed by a space

    # for line in response.iter_lines():
    #     data = line.decode("utf-8")
    #     # if data == "[DONE]":  # type: ignore
    #     #     break
    #     # if not data:
    #     #     continue
    #     # data = json.loads(data)  # type: ignore
    #     # delta = data["choices"][0]["delta"]  # type: ignore
    #     # if "content" not in delta:
    #     #     continue
    #     yield data

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 1,
        top_probability: float = 1,
        caching: bool = True,
    ) -> Generator[str, None, None]:
        """
        Generates single completion for prompt (message).

        :param messages: List of dict with messages and roles.
        :param model: String gpt-3.5-turbo or gpt-3.5-turbo-0301.
        :param temperature: Float in 0.0 - 1.0 range.
        :param top_probability: Float in 0.0 - 1.0 range.
        :param caching: Boolean value to enable/disable caching.
        :return: String generated completion.
        """
        yield from self._request(
            messages,
            model,
            temperature,
            top_probability,
            caching=caching,
        )
