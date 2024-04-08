import asyncio

import streamlit as st
from ghost.agents import ToolUserAgent
from ghost.tools import (
    FileAppendTool,
    FileCopyTool,
    FileDeleteTool,
    FileFolderExistsTool,
    FileFolderMoveTool,
    FileReadTool,
    FileWriteTool,
    FolderCopyTool,
    FolderCreateTool,
    FolderDeleteTool,
    FolderListTool,
    FolderSearchTool,
    PythonInterpreterTool,
    TerminalTool,
)
from ghost.utils.openai import OpenAIChatLLM

tool_user = ToolUserAgent(
    chatllm=OpenAIChatLLM(),
    tools=[
        PythonInterpreterTool(),
        TerminalTool(),
        FileAppendTool(),
        FileCopyTool(),
        FileDeleteTool(),
        FileFolderExistsTool(),
        FileFolderMoveTool(),
        FileReadTool(),
        FileWriteTool(),
        FolderCopyTool(),
        FolderCreateTool(),
        FolderDeleteTool(),
        FolderListTool(),
        FolderSearchTool(),
        PythonInterpreterTool(),
        TerminalTool(),
    ],
)


def reply_to_intent_9(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return """I have access to tools to create, delete, copy, move, search, list and read files and folders.I can run python and shell code"""
    elif st.session_state.pair_index == 1:
        resp = asyncio.run(tool_user(prompt))
        return resp.output
