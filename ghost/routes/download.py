import asyncio
import os
import urllib.parse
from typing import List

import streamlit as st
from ghost.utils.openai import OpenAIChatLLM
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# Set up Firefox options for headless mode
options = Options()
options.headless = True

url_list = [
    "https://fastapi.tiangolo.com/",
    "https://fastapi.tiangolo.com/advanced/",
    "https://fastapi.tiangolo.com/advanced/additional-responses/",
    "https://fastapi.tiangolo.com/advanced/additional-status-codes/",
    "https://fastapi.tiangolo.com/advanced/advanced-dependencies/",
    "https://fastapi.tiangolo.com/advanced/async-sql-databases/",
    "https://fastapi.tiangolo.com/advanced/async-tests/",
    "https://fastapi.tiangolo.com/advanced/behind-a-proxy/",
    "https://fastapi.tiangolo.com/advanced/conditional-openapi/",
    "https://fastapi.tiangolo.com/advanced/custom-request-and-route/",
    "https://fastapi.tiangolo.com/advanced/custom-response/",
    "https://fastapi.tiangolo.com/advanced/dataclasses/",
    "https://fastapi.tiangolo.com/advanced/events/",
    "https://fastapi.tiangolo.com/advanced/extending-openapi/",
    "https://fastapi.tiangolo.com/advanced/generate-clients/",
    "https://fastapi.tiangolo.com/advanced/graphql/",
    "https://fastapi.tiangolo.com/advanced/middleware/",
    "https://fastapi.tiangolo.com/advanced/nosql-databases/",
    "https://fastapi.tiangolo.com/advanced/openapi-callbacks/",
    "https://fastapi.tiangolo.com/advanced/openapi-webhooks/",
    "https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/",
    "https://fastapi.tiangolo.com/advanced/response-change-status-code/",
    "https://fastapi.tiangolo.com/advanced/response-cookies/",
    "https://fastapi.tiangolo.com/advanced/response-directly/",
    "https://fastapi.tiangolo.com/advanced/response-headers/",
    "https://fastapi.tiangolo.com/advanced/security/",
    "https://fastapi.tiangolo.com/advanced/security/http-basic-auth/",
    "https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/",
    "https://fastapi.tiangolo.com/advanced/settings/",
    "https://fastapi.tiangolo.com/advanced/sql-databases-peewee/",
    "https://fastapi.tiangolo.com/advanced/sub-applications/",
    "https://fastapi.tiangolo.com/advanced/templates/",
    "https://fastapi.tiangolo.com/advanced/testing-database/",
    "https://fastapi.tiangolo.com/advanced/testing-dependencies/",
    "https://fastapi.tiangolo.com/advanced/testing-events/",
    "https://fastapi.tiangolo.com/advanced/testing-websockets/",
    "https://fastapi.tiangolo.com/advanced/using-request-directly/",
    "https://fastapi.tiangolo.com/advanced/websockets/",
    "https://fastapi.tiangolo.com/advanced/wsgi/",
    "https://fastapi.tiangolo.com/alternatives/",
    "https://fastapi.tiangolo.com/async/",
    "https://fastapi.tiangolo.com/benchmarks/",
    "https://fastapi.tiangolo.com/contributing/",
    "https://fastapi.tiangolo.com/deployment/",
    "https://fastapi.tiangolo.com/deployment/concepts/",
    "https://fastapi.tiangolo.com/deployment/deta/",
    "https://fastapi.tiangolo.com/deployment/docker/",
    "https://fastapi.tiangolo.com/deployment/https/",
    "https://fastapi.tiangolo.com/deployment/manually/",
    "https://fastapi.tiangolo.com/deployment/server-workers/",
    "https://fastapi.tiangolo.com/deployment/versions/",
    "https://fastapi.tiangolo.com/external-links/",
    "https://fastapi.tiangolo.com/fastapi-people/",
    "https://fastapi.tiangolo.com/features/",
    "https://fastapi.tiangolo.com/help-fastapi/",
    "https://fastapi.tiangolo.com/history-design-future/",
    "https://fastapi.tiangolo.com/newsletter/",
    "https://fastapi.tiangolo.com/project-generation/",
    "https://fastapi.tiangolo.com/python-types/",
    "https://fastapi.tiangolo.com/release-notes/",
    "https://fastapi.tiangolo.com/tutorial/",
    "https://fastapi.tiangolo.com/tutorial/background-tasks/",
    "https://fastapi.tiangolo.com/tutorial/bigger-applications/",
    "https://fastapi.tiangolo.com/tutorial/body-fields/",
    "https://fastapi.tiangolo.com/tutorial/body-multiple-params/",
    "https://fastapi.tiangolo.com/tutorial/body-nested-models/",
    "https://fastapi.tiangolo.com/tutorial/body-updates/",
    "https://fastapi.tiangolo.com/tutorial/body/",
    "https://fastapi.tiangolo.com/tutorial/cookie-params/",
    "https://fastapi.tiangolo.com/tutorial/cors/",
    "https://fastapi.tiangolo.com/tutorial/debugging/",
    "https://fastapi.tiangolo.com/tutorial/dependencies/",
    "https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/",
    "https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/",
    "https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/",
    "https://fastapi.tiangolo.com/tutorial/dependencies/global-dependencies/",
    "https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/",
    "https://fastapi.tiangolo.com/tutorial/encoder/",
    "https://fastapi.tiangolo.com/tutorial/extra-data-types/",
    "https://fastapi.tiangolo.com/tutorial/extra-models/",
    "https://fastapi.tiangolo.com/tutorial/first-steps/",
    "https://fastapi.tiangolo.com/tutorial/handling-errors/",
    "https://fastapi.tiangolo.com/tutorial/header-params/",
    "https://fastapi.tiangolo.com/tutorial/metadata/",
    "https://fastapi.tiangolo.com/tutorial/middleware/",
    "https://fastapi.tiangolo.com/tutorial/path-operation-configuration/",
    "https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/",
    "https://fastapi.tiangolo.com/tutorial/path-params/",
    "https://fastapi.tiangolo.com/tutorial/query-params-str-validations/",
    "https://fastapi.tiangolo.com/tutorial/query-params/",
    "https://fastapi.tiangolo.com/tutorial/request-files/",
    "https://fastapi.tiangolo.com/tutorial/request-forms-and-files/",
    "https://fastapi.tiangolo.com/tutorial/request-forms/",
    "https://fastapi.tiangolo.com/tutorial/response-model/",
    "https://fastapi.tiangolo.com/tutorial/response-status-code/",
    "https://fastapi.tiangolo.com/tutorial/schema-extra-example/",
    "https://fastapi.tiangolo.com/tutorial/security/",
    "https://fastapi.tiangolo.com/tutorial/security/first-steps/",
    "https://fastapi.tiangolo.com/tutorial/security/get-current-user/",
    "https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/",
    "https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/",
    "https://fastapi.tiangolo.com/tutorial/sql-databases/",
    "https://fastapi.tiangolo.com/tutorial/static-files/",
    "https://fastapi.tiangolo.com/tutorial/testing/",
]

downloader = OpenAIChatLLM()
asyncio.run(
    downloader.set_system_prompt(
        "Create valid urls from the users query Eg: https://www.google.com, https://www.facebook.com"
    )
)


class URLList(BaseModel):
    urls: List[str] = []


def reply_to_intent_8(prompt, messages):
    if st.session_state.pair_index == 0:
        st.session_state.pair_index = 1
        return "Which urls would you like to download?"
    elif st.session_state.pair_index == 1:
        urls = asyncio.run(downloader(prompt, URLList))
        driver = webdriver.Firefox(options=options)
        for url in urls.urls:
            driver.get(url)
            path = urllib.parse.urlparse(url).path.rstrip("/")
            path = path[1:]
            if not path:
                path = "index"
            filename = path.replace("/", "-") + ".html"
            print(filename)
            os.makedirs("output/downloads", exist_ok=True)
            with open("output/downloads/" + filename, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        return urls
