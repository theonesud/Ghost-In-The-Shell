# File: client.py
import requests


def consume_stream():
    response = requests.get("http://localhost:8000/", stream=True)
    for chunk in response.iter_content(chunk_size=1):
        if (
            chunk.decode() == " "
        ):  # When a space is encountered, print the buffered word
            print()
        else:
            print(chunk.decode(), end="")


if __name__ == "__main__":
    consume_stream()
