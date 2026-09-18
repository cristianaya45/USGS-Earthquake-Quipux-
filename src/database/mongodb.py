from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from config.settings import get_settings


@lru_cache
def get_client() -> MongoClient:
    """Cliente Mongo singleton por proceso: pymongo gestiona su propio pool
    de conexiones internamente, por lo que basta con reutilizar una instancia."""
    settings = get_settings()
    return MongoClient(settings.mongo_uri)


def get_database() -> Database:
    settings = get_settings()
    return get_client()[settings.mongo_db]
