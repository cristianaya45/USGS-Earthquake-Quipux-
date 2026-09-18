import re
from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from pymongo.database import Database

from api.dependencies import get_db
from api.serializers import serialize_document
from config.constants import EARTHQUAKES_COLLECTION
from models.earthquake import EarthquakeOut

router = APIRouter(prefix="/earthquakes", tags=["earthquakes"])


class EarthquakeListResponse(BaseModel):
    items: list[EarthquakeOut]
    page: int
    page_size: int
    total: int


@router.get("", response_model=EarthquakeListResponse)
def list_earthquakes(
    db: Database = Depends(get_db),
    min_magnitude: float | None = Query(default=None, ge=-2, le=10),
    max_magnitude: float | None = Query(default=None, ge=-2, le=10),
    location: str | None = Query(default=None, max_length=200),
    sort_by: Literal["event_time", "magnitude"] = Query(default="event_time"),
    order: Literal["asc", "desc"] = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
):
    query: dict = {}
    if min_magnitude is not None or max_magnitude is not None:
        query["magnitude"] = {}
        if min_magnitude is not None:
            query["magnitude"]["$gte"] = min_magnitude
        if max_magnitude is not None:
            query["magnitude"]["$lte"] = max_magnitude
    if location:
        query["location"] = {"$regex": re.escape(location), "$options": "i"}

    sort_direction = -1 if order == "desc" else 1
    skip = (page - 1) * page_size

    collection = db[EARTHQUAKES_COLLECTION]
    cursor = collection.find(query).sort(sort_by, sort_direction).skip(skip).limit(page_size)

    return {
        "items": [serialize_document(doc) for doc in cursor],
        "page": page,
        "page_size": page_size,
        "total": collection.count_documents(query),
    }
