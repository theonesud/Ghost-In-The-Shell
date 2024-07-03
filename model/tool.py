from typing import Any, List, Literal, Optional

from pydantic import BaseModel


class Param(BaseModel):
    name: str
    desc: str


class Output(BaseModel):
    output: Any
    exit_code: Literal[0, 1] = 0


class Tool(BaseModel):
    name: str
    desc: str
    params: Optional[List[Param]] = None
    output: Optional[Output] = None


class Tools(BaseModel):
    tools: List[Tool]


available_tools = Tools(
    tools=[
        Tool(
            name="File Read",
            desc="Reads a file and returns its contents.",
            params=[
                Param(
                    name="file_path", desc="The path to the file to be read (type: str)"
                ),
                Param(
                    name="encoding",
                    desc="The encoding of the file, defaults to utf-8 (type: str)",
                ),
            ],
        ),
        Tool(
            name="File Write",
            desc="Writes the provided contents to a file, overwrites if it.",
            params=[
                Param(
                    name="file_path",
                    desc="The path to the file to be written to (type: str)",
                ),
                Param(
                    name="content",
                    desc="The content to be written to the file (type: str)",
                ),
                Param(
                    name="encoding",
                    desc="The encoding of the file, defaults to utf-8 (type: str)",
                ),
            ],
        ),
        Tool(
            name="File Append",
            desc="Appends the provided contents to a file, creates if it doesn't exist.",
            params=[
                Param(
                    name="file_path",
                    desc="The path to the file to be appended to (type: str)",
                ),
                Param(
                    name="content",
                    desc="The content to be appended to the file (type: str)",
                ),
                Param(
                    name="encoding",
                    desc="The encoding of the file, defaults to utf-8 (type: str)",
                ),
            ],
        ),
        Tool(
            name="File Delete",
            desc="Deletes the requested file. Asks for confirmation before deleting.",
            params=[
                Param(
                    name="file_path",
                    desc="The path to the file to be deleted (type: str)",
                ),
            ],
        ),
        Tool(
            name="File / Folder Move",
            desc="Moves a file or a folder from one location to another. Can also be used to rename a file or folder.",
            params=[
                Param(
                    name="src",
                    desc="The path to the file or folder to be moved (type: str)",
                ),
                Param(
                    name="destination", desc="The path to the destination (type: str)"
                ),
            ],
        ),
        Tool(
            name="File Copy",
            desc="Copies a file from one location to another, overwrites if destination exists.",
            params=[
                Param(
                    name="file_path",
                    desc="The path to the file to be copied (type: str)",
                ),
                Param(
                    name="destination", desc="The path to the destination (type: str)"
                ),
            ],
        ),
        Tool(
            name="File / Folder Exists",
            desc="Check if a file or folder exists.",
            params=[
                Param(
                    name="path",
                    desc="The path to the file or folder to be checked (type: str)",
                ),
            ],
        ),
        Tool(
            name="Folder Search",
            desc="Searches for the location of a requested file in a folder and its subfolders.",
            params=[
                Param(
                    name="folder",
                    desc="The path to the folder to be searched (type: str)",
                ),
                Param(
                    name="filename",
                    desc="The name of the file to be searched for (type: str)",
                ),
            ],
        ),
        Tool(
            name="Folder Create",
            desc="Creates a folder, ignores if it exists.",
            params=[
                Param(
                    name="folder",
                    desc="The path to the folder to be created (type: str)",
                ),
            ],
        ),
        Tool(
            name="Folder Delete",
            desc="Deletes the requested folder and its contents, ignores if it doesn't exist. Asks for confirmation before deleting.",
            params=[
                Param(
                    name="folder",
                    desc="The path to the folder to be deleted (type: str)",
                ),
            ],
        ),
        Tool(
            name="Folder Copy",
            desc="Copies a folder from one location to another.",
            params=[
                Param(
                    name="folder",
                    desc="The path to the folder to be copied (type: str)",
                ),
                Param(
                    name="destination", desc="The path to the destination (type: str)"
                ),
            ],
        ),
        Tool(
            name="Folder List",
            desc="Lists the contents of the requested folder.",
            params=[
                Param(
                    name="folder",
                    desc="The path to the folder to be listed (type: str)",
                ),
            ],
        ),
        Tool(
            name="Python Interpreter",
            desc="Runs the provided python code in the current interpreter",
            params=[
                Param(name="code", desc="Python code to be run (type: str)"),
                Param(
                    name="vars",
                    desc="A python dictionary containing variables to be passed to the code",
                ),
                Param(
                    name="timeout",
                    desc="Timeout in seconds (type: int). Defaults to 60.",
                ),
            ],
        ),
        Tool(
            name="Terminal",
            desc="Run the provided commands in the shell",
            params=[
                Param(
                    name="command",
                    desc="The terminal command to be run (type: str)",
                ),
                Param(
                    name="executable",
                    desc="The executable to run the command with (type: str). Defaults to /bin/sh",
                ),
                Param(
                    name="timeout",
                    desc="Timeout in seconds (type: int). Defaults to 60.",
                ),
            ],
        ),
    ]
)
