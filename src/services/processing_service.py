import logging
from datetime import datetime, timedelta, timezone

from pymongo.database import Database

from config.constants import EARTHQUAKES_COLLECTION, HOUR_WINDOW_FORMAT, MAGNITUDE_RANGES, METRICS_COLLECTION
from models.earthquake import EarthquakeCreate

logger = logging.getLogger(__name__)


class ProcessingService:
    """Recalcula las métricas en tiempo real de las ventanas horarias afectadas
    por los eventos recién ingeridos. Recalcular por agregación (en vez de
    incrementar contadores) mantiene avg/max/distribución siempre consistentes
    con lo almacenado, sin arrastrar errores de redondeo entre ciclos."""

    def __init__(self, db: Database):
        self._db = db

    def update_metrics(self, events: list[EarthquakeCreate]) -> None:
        windows = {event.event_time.strftime(HOUR_WINDOW_FORMAT) for event in events}
        for window in windows:
            self._recompute_window(window)

    def _recompute_window(self, window: str) -> None:
        start, end = self._window_bounds(window)
        pipeline = [
            {"$match": {"event_time": {"$gte": start, "$lt": end}}},
            {
                "$group": {
                    "_id": None,
                    "count": {"$sum": 1},
                    "avg_magnitude": {"$avg": "$magnitude"},
                    "max_magnitude": {"$max": "$magnitude"},
                    "magnitudes": {"$push": "$magnitude"},
                }
            },
        ]
        result = list(self._db[EARTHQUAKES_COLLECTION].aggregate(pipeline))
        if not result:
            return

        stats = result[0]
        self._db[METRICS_COLLECTION].find_one_and_update(
            {"window": window},
            {
                "$set": {
                    "window": window,
                    "earthquake_count": stats["count"],
                    "avg_magnitude": round(stats["avg_magnitude"], 3),
                    "max_magnitude": stats["max_magnitude"],
                    "magnitude_distribution": self._build_distribution(stats["magnitudes"]),
                }
            },
            upsert=True,
        )
        logger.info("metrics_updated", extra={"window": window, "count": stats["count"]})

    @staticmethod
    def _window_bounds(window: str) -> tuple[datetime, datetime]:
        start = datetime.strptime(window, HOUR_WINDOW_FORMAT).replace(tzinfo=timezone.utc)
        return start, start + timedelta(hours=1)

    @staticmethod
    def _build_distribution(magnitudes: list[float]) -> dict:
        distribution = {name: 0 for name, _, _ in MAGNITUDE_RANGES}
        for magnitude in magnitudes:
            for name, low, high in MAGNITUDE_RANGES:
                if low <= magnitude < high:
                    distribution[name] += 1
                    break
        return distribution
