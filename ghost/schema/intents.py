from typing import List

from pydantic import BaseModel, Field


class TagResp(BaseModel):
    tags: List[str]


class PythonCode(BaseModel):
    code: str = Field(description="Python code in the format ````python\ncode\n```")


class CodeResp(BaseModel):
    file_location: str = Field(
        description="File location based on the template location"
    )
    code: str = Field(
        description="Python code inside a codeblock like ```python\n# code here\n```"
    )


class PathResp(BaseModel):
    path: str = Field(description="Path to the file based on the template location")


class URLList(BaseModel):
    urls: List[str] = []
