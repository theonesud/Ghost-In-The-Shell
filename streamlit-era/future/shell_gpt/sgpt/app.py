import asyncio
import json
import os
import readline
import sys  # noqa: F401
import uuid

import prompt_toolkit
import typer
from click import BadArgumentUsage
from click.types import Choice
from ghost.tools import PythonInterpreterTool, TerminalTool
from prompt_toolkit.history import FileHistory

from sgpt.config import cfg
from sgpt.handlers.chat_handler import CHAT_CACHE_PATH, ChatHandler
from sgpt.role import DefaultRoles, SystemRole
from sgpt.utils import run_command

history = FileHistory(".command_history")


def main(
    prompt: str = typer.Argument(
        None,
        show_default=False,
        help="The prompt to generate completions for",
    ),
    python: bool = typer.Option(
        False,
        "--python",
        "-p",
        help="Generate and run python code",
        rich_help_panel="Usage Modes",
    ),
    shell: bool = typer.Option(
        False,
        "--shell",
        "-s",
        help="Generate and execute shell commands.",
        rich_help_panel="Usage Modes",
    ),
    run: bool = typer.Option(
        False,
        "--run",
        "-r",
        help="Run python code or shell commands. Requires --python or --shell",
        rich_help_panel="Usage Modes",
    ),
    chat: bool = typer.Option(
        False,
        "--chat",
        "-c",
        help="Talk to it normally",
        rich_help_panel="Usage Modes",
    ),
    model: str = typer.Option(
        cfg.get("DEFAULT_MODEL"),
        help="Large language model to use.",
        rich_help_panel="Model Options",
    ),
    temperature: float = typer.Option(
        0.1,
        min=0.0,
        max=2.0,
        help="Randomness of generated output.",
        rich_help_panel="Model Options",
    ),
    top_probability: float = typer.Option(
        1.0,
        min=0.1,
        max=1.0,
        help="Limits highest probable tokens (words).",
        rich_help_panel="Model Options",
    ),
    cache: bool = typer.Option(
        True,
        help="Cache completion results.",
        rich_help_panel="Advanced Options",
    ),
    chatid: str = typer.Option(
        None,
        help="Follow conversation with id, " 'use "temp" for quick session.',
        rich_help_panel="Advanced Options",
    ),
    show_chat: str = typer.Option(
        None,
        help="Show all messages from provided chat id.",
        callback=ChatHandler.show_messages_callback,
        rich_help_panel="Advanced Options",
    ),
    list_chats: bool = typer.Option(
        False,
        help="List all existing chat ids.",
        callback=ChatHandler.list_ids,
        rich_help_panel="Advanced Options",
    ),
) -> None:
    stdin_passed = not sys.stdin.isatty()

    if python and shell:
        raise BadArgumentUsage("--code and --shell options cannot be used together.")

    states = []

    if os.path.exists(f"{CHAT_CACHE_PATH}/{chatid}.json"):
        # if os.path.pardir exists(f"{CHAT_CACHE_PATH}/{chatid}.json"):
        with open(f"{CHAT_CACHE_PATH}/{chatid}.json", "r") as f:
            states = json.load(f)["states"]
    for index, message in enumerate(states):
        message = "\n".join([f"{k.upper()}: {v}" for k, v in message.items()])
        color = "green" if index % 2 == 0 else "magenta"
        typer.secho(message, fg=color)

    def normal_chat():
        role_class = DefaultRoles.DEFAULT.get_role()
        full_completion = ChatHandler(chatid + "default", role_class).handle(
            prompt,
            model=model,
            temperature=temperature,
            top_probability=top_probability,
            chat_id=chatid,
            caching=cache,
        )
        states.append({"request": prompt, "output": full_completion})

    def run_code(save=True, run=True):
        role_class = DefaultRoles.CODE.get_role()
        full_completion = ChatHandler(chatid + "code", role_class).handle(
            prompt[3:] if not python and not shell else prompt,
            model=model,
            temperature=temperature,
            top_probability=top_probability,
            chat_id=chatid,
            caching=cache,
        )
        if not save and not run:
            return full_completion
        states.append(
            {
                "code_request": prompt[3:] if not python and not shell else prompt,
                "code": full_completion,
            }
        )
        option = typer.prompt(
            text="Run? y/[n]",
            type=Choice(("n", "y"), case_sensitive=False),
            default="n",
            show_choices=False,
            show_default=False,
        )
        if option in ("y"):
            pyshell = PythonInterpreterTool()
            output = asyncio.run(pyshell(full_completion))
            states.append(
                {
                    "code_request": prompt[3:] if not python and not shell else prompt,
                    "code": full_completion,
                    "output": output.output,
                }
            )
        option = typer.prompt(
            text="Save? y/[n]",
            type=Choice(("n", "y"), case_sensitive=False),
            default="n",
            show_choices=False,
            show_default=False,
        )
        if option in ("y"):
            filename = input("Filename: ")
            with open(filename, "a") as f:
                f.write(full_completion)
                typer.echo(f"Saved to {filename}")

    def run_shell(run=True):
        role_class = DefaultRoles.SHELL.get_role()
        full_completion = ChatHandler(chatid + "shell", role_class).handle(
            prompt[3:] if not python and not shell else prompt,
            model=model,
            temperature=temperature,
            top_probability=top_probability,
            chat_id=chatid,
            caching=cache,
        )
        if not run:
            return full_completion
        states.append(
            {
                "shell_request": prompt[3:] if not python and not shell else prompt,
                "shell": full_completion,
                # "output": output
            }
        )
        option = typer.prompt(
            text="Run? y/[n]",
            type=Choice(("n", "y"), case_sensitive=False),
            default="n",
            show_choices=False,
            show_default=False,
        )
        if option in ("y"):
            # run_command(full_completion)
            shelltool = TerminalTool()
            output = asyncio.run(shelltool(full_completion))
            states.append(
                {
                    "shell_request": prompt[3:] if not python and not shell else prompt,
                    "shell": full_completion,
                    "output": output.output,
                }
            )

    if python:
        if not prompt:
            raise BadArgumentUsage("Prompt is required for --code option.")
        if not chatid:
            chatid = str(uuid.uuid4())
        if stdin_passed:
            prompt = f"{sys.stdin.read()}\n\n{prompt or ''}"
        return run_code(save=False, run=run)
    if shell:
        if not chatid:
            chatid = str(uuid.uuid4())
        if not prompt:
            raise BadArgumentUsage("Prompt is required for --shell option.")
        if stdin_passed:
            prompt = f"{sys.stdin.read()}\n\n{prompt or ''}"
        return run_shell(run=run)
    if chat:
        if not chatid:
            chatid = str(uuid.uuid4())
        if not prompt:
            raise BadArgumentUsage("Prompt is required for --chat option.")
        if stdin_passed:
            prompt = f"{sys.stdin.read()}\n\n{prompt or ''}"
        return normal_chat()
    if not python and not shell and not chat:
        # Will be in infinite loop here until user exits with Ctrl+C.
        try:
            print(
                'Welcome to the Natural Language Terminal\nAsk anything about the world\nStart with "$p " to write and run python code\nStart with "$s " to write and run shell commands'
            )
            while True:
                prompt = prompt_toolkit.prompt(">>> ", history=history)

                if not chatid:
                    role_class = DefaultRoles.DEFAULT.get_role()
                    full_completion = ChatHandler(str(uuid.uuid4()), role_class).handle(
                        f"Generate a very short title for a chat that starts with : {prompt[:100]}. Be Concise. Reply with the title and nothing else",
                        model=model,
                        temperature=temperature,
                        top_probability=top_probability,
                        chat_id=str(uuid.uuid4()),
                        caching=cache,
                    )
                    chatid = full_completion

                # Write / Run / Save Code
                if prompt.startswith("$p "):
                    run_code()
                # Write / Run Shell Command
                elif prompt.startswith("$s "):
                    run_shell()
                # Chat
                else:
                    normal_chat()
        except KeyboardInterrupt:
            with open(f"{CHAT_CACHE_PATH}/{chatid}.json", "w") as f:
                json.dump({"states": states}, f)
            typer.echo("Saving chat history...")


def entry_point() -> None:
    typer.run(main)


if __name__ == "__main__":
    entry_point()
