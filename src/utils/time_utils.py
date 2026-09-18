from datetime import datetime, timedelta, timezone


def previous_hour_start(reference: datetime | None = None) -> datetime:
    reference = reference or datetime.now(timezone.utc)
    current_hour = reference.replace(minute=0, second=0, microsecond=0)
    return current_hour - timedelta(hours=1)
