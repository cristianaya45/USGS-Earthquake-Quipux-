from pymongo.database import Database

from database.mongodb import get_database


def get_db() -> Database:
    return get_database()
