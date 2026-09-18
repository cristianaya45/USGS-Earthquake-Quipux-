from datetime import datetime, timezone

from pydantic import BaseModel, field_validator

from metadata.validators import validate_latitude, validate_longitude, validate_magnitude


class EarthquakeCreate(BaseModel):
    event_id: str
    magnitude: float
    location: str
    latitude: float
    longitude: float
    depth: float
    event_time: datetime

    @field_validator("magnitude")
    @classmethod
    def _check_magnitude(cls, value: float) -> float:
        return validate_magnitude(value)

    @field_validator("latitude")
    @classmethod
    def _check_latitude(cls, value: float) -> float:
        return validate_latitude(value)

    @field_validator("longitude")
    @classmethod
    def _check_longitude(cls, value: float) -> float:
        return validate_longitude(value)


def from_usgs_feature(feature: dict) -> EarthquakeCreate:
    properties = feature["properties"]
    coordinates = feature["geometry"]["coordinates"]

    return EarthquakeCreate(
        event_id=feature["id"],
        magnitude=properties["mag"],
        location=properties.get("place") or "unknown",
        latitude=coordinates[1],
        longitude=coordinates[0],
        depth=coordinates[2] if len(coordinates) > 2 else 0.0,
        event_time=datetime.fromtimestamp(properties["time"] / 1000, tz=timezone.utc),
    )
