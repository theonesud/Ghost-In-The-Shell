from flows.audio import analyse_audio
from flows.db import retrieve_from_vector_db
from flows.image import generate_image, understand_image
from flows.os import call_a_function, call_an_api, open_browser, use_terminal

task_handlers = {
    "generate_image": generate_image,
    "understand_image": understand_image,
    "analyse_audio": analyse_audio,
    "retrieve_from_vector_db": retrieve_from_vector_db,
    "call_a_function": call_a_function,
    "call_an_api": call_an_api,
    "open_browser": open_browser,
    "use_terminal": use_terminal,
}
