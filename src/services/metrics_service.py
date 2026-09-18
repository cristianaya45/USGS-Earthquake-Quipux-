from pymongo.database import Database

from config.constants import METRICS_COLLECTION


class MetricsService:
    def __init__(self, db: Database):
        self._db = db

    def list_metrics(self, window: str | None = None, limit: int = 50, skip: int = 0) -> list[dict]:
        query = {"window": window} if window else {}
        cursor = self._db[METRICS_COLLECTION].find(query).sort("window", -1).skip(skip).limit(limit)
        return list(cursor)

    def count(self, window: str | None = None) -> int:
        query = {"window": window} if window else {}
        return self._db[METRICS_COLLECTION].count_documents(query)
