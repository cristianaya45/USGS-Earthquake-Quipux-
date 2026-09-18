import logging

from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from clients.usgs_client import UsgsClient
from config.constants import EARTHQUAKES_COLLECTION
from models.earthquake import EarthquakeCreate, from_usgs_feature
from services.processing_service import ProcessingService

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, db: Database, usgs_client: UsgsClient, processing_service: ProcessingService):
        self._db = db
        self._usgs_client = usgs_client
        self._processing_service = processing_service

    def run_once(self) -> int:
        features = self._usgs_client.fetch_features()
        new_events: list[EarthquakeCreate] = []

        for feature in features:
            if feature.get("properties", {}).get("mag") is None:
                continue

            try:
                earthquake = from_usgs_feature(feature)
            except (ValueError, KeyError) as exc:
                logger.warning(
                    "invalid_feature_skipped",
                    extra={"feature_id": feature.get("id"), "error": str(exc)},
                )
                continue

            if self._insert_if_new(earthquake):
                new_events.append(earthquake)

        if new_events:
            self._processing_service.update_metrics(new_events)

        logger.info("ingestion_cycle_complete", extra={"new_events": len(new_events), "fetched": len(features)})
        return len(new_events)

    def _insert_if_new(self, earthquake: EarthquakeCreate) -> bool:
        try:
            self._db[EARTHQUAKES_COLLECTION].insert_one(earthquake.model_dump())
            return True
        except DuplicateKeyError:
            return False
