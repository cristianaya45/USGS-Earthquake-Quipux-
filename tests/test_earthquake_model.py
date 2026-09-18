import pytest
from pydantic import ValidationError

from models.earthquake import from_usgs_feature

FEATURE = {
    "id": "us7000xxxx",
    "properties": {"mag": 4.2, "place": "20 km NW of California", "time": 1718610000000},
    "geometry": {"coordinates": [-120.12, 35.44, 10.5]},
}


def test_from_usgs_feature_maps_fields_correctly():
    earthquake = from_usgs_feature(FEATURE)
    assert earthquake.event_id == "us7000xxxx"
    assert earthquake.magnitude == 4.2
    assert earthquake.latitude == 35.44
    assert earthquake.longitude == -120.12
    assert earthquake.depth == 10.5


def test_from_usgs_feature_defaults_missing_place():
    feature = {**FEATURE, "properties": {**FEATURE["properties"], "place": None}}
    earthquake = from_usgs_feature(feature)
    assert earthquake.location == "unknown"


def test_from_usgs_feature_rejects_invalid_magnitude():
    feature = {**FEATURE, "properties": {**FEATURE["properties"], "mag": 999}}
    with pytest.raises(ValidationError):
        from_usgs_feature(feature)
