import asyncio
from ghost.core.tool import Tool
from ghost.schema.tool import ParamDocumentation, ToolDocumentation, ToolReturn
from ghost.utils.openai import OpenAIChatLLM
from ghost.schema.persona import Persona

global_ai = None

class TerminalTool(Tool):
    def __init__(self):
        super().__init__(
            docs=ToolDocumentation(
                name="Persona",
                desc="Act as a specific persona",
                params=[
                    ParamDocumentation(
                        name="persona",
                        desc="The persona code to run (type: str)",
                    ),
                ],
            )
        )
        self.ai = OpenAIChatLLM()
        asyncio.run(self.ai.set_system_prompt(
            Persona.
        ))

    async def _run(self, prompt: str) -> ToolReturn:
        await self.ai(prompt)
        # def reply_to_intent_10(prompt, messages):
        #     if st.session_state.pair_index == 0:
        #         st.session_state.pair_index = 1
        #         return "Enter a gpt prompt you want to improve"
        #     elif st.session_state.pair_index == 1:
        #         meta =
        #         return meta

        # process = await asyncio.create_subprocess_shell(
        #     command,
        #     executable=executable,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        # )
        # try:
        #     stdout, stderr = await asyncio.wait_for(
        #         process.communicate(), timeout=timeout
        #     )
        # except asyncio.TimeoutError:
        #     process.kill()
        #     raise
        if process.returncode != 0:
            return ToolReturn(output=stderr.decode(), exit_code=1)
        else:
            return ToolReturn(output=stdout.decode(), exit_code=0)
