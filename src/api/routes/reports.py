from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from api.dependencies import get_db
from api.serializers import serialize_document
from services.reporting_service import ReportingService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
def list_reports(
    limit: int = Query(default=50, ge=1, le=200),
    skip: int = Query(default=0, ge=0),
    db: Database = Depends(get_db),
):
    service = ReportingService(db)
    items = service.list_reports(limit=limit, skip=skip)
    return {"items": [serialize_document(doc) for doc in items]}
