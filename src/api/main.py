import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import earthquakes, metrics, reports
from config.logging import configure_logging
from database.indexes import ensure_indexes
from database.mongodb import get_database

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_indexes(get_database())
    logger.info("api_startup_complete")
    yield


app = FastAPI(title="USGS Earthquake API", version="1.0.0", lifespan=lifespan)

app.include_router(earthquakes.router)
app.include_router(metrics.router)
app.include_router(reports.router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
