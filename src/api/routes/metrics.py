from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from pymongo.database import Database

from api.dependencies import get_db
from api.serializers import serialize_document
from models.metric import MetricWindow
from services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


class MetricListResponse(BaseModel):
    items: list[MetricWindow]
    total: int


@router.get("", response_model=MetricListResponse)
def list_metrics(
    window: str | None = Query(default=None, description="Ventana horaria, ej. 2026-06-17T10"),
    limit: int = Query(default=50, ge=1, le=200),
    skip: int = Query(default=0, ge=0),
    db: Database = Depends(get_db),
):
    service = MetricsService(db)
    items = service.list_metrics(window=window, limit=limit, skip=skip)
    return {
        "items": [serialize_document(doc) for doc in items],
        "total": service.count(window=window),
    }
