from tinydb import TinyDB

db_instance = TinyDB("db.json")


def get_db():
    return db_instance
