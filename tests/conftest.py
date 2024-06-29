import pytest
from tinydb import TinyDB
from db_util import get_db


@pytest.fixture(scope="function", autouse=True)
def db():
    # Set up the database for testing
    db = TinyDB("test_db.json")
    db.drop_tables()

    # Insert a mock chat into the database
    chat_id = "test_chat_id"
    db.table("chats").insert(
        {
            "chat_id": chat_id,
            "messages": [
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi! How can I help you?"},
            ],
        }
    )

    # Inject the test database into the FastAPI app
    get_db.db_instance = db

    yield db

    # Teardown the database after each test
    db.drop_tables()
