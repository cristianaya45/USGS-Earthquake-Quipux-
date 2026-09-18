import logging
import time

from clients.usgs_client import UsgsClient
from config.logging import configure_logging
from config.settings import get_settings
from database.indexes import ensure_indexes
from database.mongodb import get_database
from services.ingestion_service import IngestionService
from services.processing_service import ProcessingService

configure_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    db = get_database()
    ensure_indexes(db)

    ingestion_service = IngestionService(
        db=db,
        usgs_client=UsgsClient(),
        processing_service=ProcessingService(db),
    )

    logger.info("ingestion_loop_start", extra={"interval_seconds": settings.ingestion_interval_seconds})
    while True:
        try:
            ingestion_service.run_once()
        except Exception:
            logger.exception("ingestion_cycle_failed")
        time.sleep(settings.ingestion_interval_seconds)


if __name__ == "__main__":
    main()
