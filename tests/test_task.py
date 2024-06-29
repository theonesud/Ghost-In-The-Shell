import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_task():
    response = client.post("/tasks/", json={"task_data": "data"})
    assert response.status_code == 200


def test_get_tasks():
    response = client.get("/tasks/")
    assert response.status_code == 200
