from tinydb import TinyDB


def get_db():
    return TinyDB("db.json")
