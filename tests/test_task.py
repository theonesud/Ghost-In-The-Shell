import pprint
import pytest
import requests


def test_create_task():
    url = "http://0.0.0.0:8000/tasks/create"
    data = {"name": "Sud", "description": "The Great"}
    response = requests.post(url, json=data)
    assert response.status_code == 200
