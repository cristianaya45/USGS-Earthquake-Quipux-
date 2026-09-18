import logging
from collections import Counter
from datetime import datetime, timedelta

from pymongo.database import Database

from config.constants import EARTHQUAKES_COLLECTION, HOURLY_REPORTS_COLLECTION

logger = logging.getLogger(__name__)


class ReportingService:
    """Genera y consulta los reportes horarios consolidados. La generación la
    dispara el DAG de Airflow; la consulta la expone la API en /reports."""

    def __init__(self, db: Database):
        self._db = db

    def generate_hourly_report(self, hour_start: datetime) -> dict:
        hour_end = hour_start + timedelta(hours=1)
        pipeline = [
            {"$match": {"event_time": {"$gte": hour_start, "$lt": hour_end}}},
            {
                "$group": {
                    "_id": None,
                    "total_events": {"$sum": 1},
                    "average_magnitude": {"$avg": "$magnitude"},
                    "max_magnitude": {"$max": "$magnitude"},
                    "locations": {"$push": "$location"},
                }
            },
        ]
        result = list(self._db[EARTHQUAKES_COLLECTION].aggregate(pipeline))

        report = {
            "report_date": hour_start,
            "total_events": 0,
            "average_magnitude": 0.0,
            "max_magnitude": 0.0,
            "top_locations": [],
        }

        if result:
            stats = result[0]
            report.update(
                total_events=stats["total_events"],
                average_magnitude=round(stats["average_magnitude"], 3),
                max_magnitude=stats["max_magnitude"],
                top_locations=self._top_locations(stats["locations"]),
            )

        self._db[HOURLY_REPORTS_COLLECTION].find_one_and_update(
            {"report_date": hour_start},
            {"$set": report},
            upsert=True,
        )
        logger.info(
            "hourly_report_generated",
            extra={"report_date": hour_start.isoformat(), "total_events": report["total_events"]},
        )
        return report

    def list_reports(self, limit: int = 50, skip: int = 0) -> list[dict]:
        cursor = self._db[HOURLY_REPORTS_COLLECTION].find().sort("report_date", -1).skip(skip).limit(limit)
        return list(cursor)

    @staticmethod
    def _top_locations(locations: list[str], top_n: int = 3) -> list[str]:
        return [location for location, _ in Counter(locations).most_common(top_n)]
