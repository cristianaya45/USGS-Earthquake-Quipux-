from datetime import datetime

from pydantic import BaseModel


class HourlyReport(BaseModel):
    id: str
    report_date: datetime
    total_events: int
    average_magnitude: float
    max_magnitude: float
    top_locations: list[str]
