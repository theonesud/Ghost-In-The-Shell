import asyncio
import os
from pathlib import Path

import streamlit as st
from ghost.utils.openai import OpenAIChatLLM
from pydantic import BaseModel, Field

ai = OpenAIChatLLM()


# def respond(prompt, chat_history):
#     if prompt.startswith("@"):
#         return
#     elif len(chat_history) > 2 and not chat_history[-2]["content"].startswith("#prd"):
#         return create_prd(chat_history)
#     elif prompt.startswith("#prd"):
#         ask_prd_questions(chat_history)
#     else:
#         return ai(
#             "You are a god, only respond as someone who knows the entire existence",
#             chat_history,
#         )


class CodeResp(BaseModel):
    file_location: str = Field(
        description="File location based on the template location"
    )
    code: str = Field(
        description="Python code inside a codeblock like ```python\n# code here\n```"
    )


class PathResp(BaseModel):
    path: str = Field(description="Path to the file based on the template location")


def reply_to_intent_3(prompt, messages):
    # st.write("Sales:")
    # st.dataframe(sales_data)
    if st.session_state.pair_index == 0:
        # st.write("Catalog:")
        # st.dataframe(catalog_data)
        st.session_state.pair_index = 1
        return "Give a filename and a the contents of the file. Eg: Create a sqlalchemy db file for products, offers, inventory, and orders"
    elif st.session_state.pair_index == 1:
        pather = OpenAIChatLLM()
        asyncio.run(
            pather.set_system_prompt("""Reply with the following paths based on what the user wants to create/edit:
        api/route.py - the CRUD routes for a resource
        model/db.py - the sqlalchemy db models for a resource
        model/ql.py - the pydantic models for CRUD endpoint body verification
        scripts/run.sh - run the server locally
        scripts/deploy.sh - deploy the server
        scripts/test.sh - run pytest tests
        tests/test_route.py - test the CRUD routes
        tests/locustfile.py - test the server performance
        Dockerfile - build the docker image
        config.py - global variables and configs
        main.py - the main server
        requirements.txt - the python dependencies
        pyproject.toml - the app info
        """)
        )
        resp = asyncio.run(pather(prompt, PathResp))
        # folder = prompt[1:4].lower()
        # path = prompt.split(" ")[0][4:]
        with open(Path(f"ghost/sop/py/{resp.path}")) as f:
            code = f.read()
        coder = OpenAIChatLLM()
        asyncio.run(
            coder.set_system_prompt(
                f""""Edit this template according to the user's needs. Follow the template closely and add all the features to it without the user specifying. Be very mindful of the usecase the user is trying to achieve."
        Example Code:
        ```python
        {code}
        ```
        """
            )
        )
        resp = asyncio.run(coder(prompt, CodeResp))
        generated_code = resp.code
        file_location = resp.file_location
        generated_code = generated_code.lstrip("```python")
        generated_code = generated_code.lstrip("```")
        generated_code = generated_code.rstrip("```")
        # code = generated_code.split("```python")[1].split("```")[0]
        # if not code:
        #     code = generated_code.split("```")[1].split("```")[0]
        os.makedirs("output", exist_ok=True)
        file_location_path = Path(file_location)
        generated_loc = Path("output") / file_location_path
        generated_loc.parent.mkdir(parents=True, exist_ok=True)
        with open(generated_loc, "w") as f:
            f.write(generated_code)
        return f"```python\n{generated_code}\n```"


def reply_to_intent_4(prompt, messages):
    with open(Path("ghost/sop/prd.md"), "r") as f:
        prd = f.read()
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        asker = OpenAIChatLLM()
        asyncio.run(
            asker.set_system_prompt(f"""Your job is to create a set of questions for the user. From the answers of the questions you should be able to create a PRD like the one I've mentioned below. Ask very specific questions to the user. You should have details about the database structure, route structure, implementation details, any special requirements. Example PRD: {prd}
        """)
        )
        resp = asyncio.run(asker(prompt))
        return resp
        # return ai(
        #     f"",
        #     chat_history,
        # )
        # st.write("Sales:")
        # st.dataframe(sales_data)
        # return "Search by Vibe: Show me a beautiful dress to wear at a party"
    elif st.session_state.pair_index == 1:
        # ecom_tagger = OpenAIChatLLM()
        # ecom_tagger.set_system_prompt(
        #     f"Create the ecommerce website search tags for the user query. You can choose from the tags mentioned in this db column {catalog_data["Tags"]} Output in this format: key:'response' -> val:['tag1', 'tag2', 'tag3']"
        # )
        # tags = ecom_tagger(prompt)
        # with open(Path("sop/prd.md"), "r") as f:
        #     prd = f.read()
        prdmaster = OpenAIChatLLM()
        asyncio.run(
            prdmaster.set_system_prompt(
                f"Create a PRD based on the given structure and the user's requirements. It should have details about the database structure, route structure, implementation details, any special requirements. Example PRD Structure: {prd}"
            )
        )
        resp = asyncio.run(prdmaster(prompt))
        with open(Path("output/prd.md"), "w") as f:
            f.write(resp)
        return resp
        # return search_catalog(tags, catalog_data)
