from pymongo.errors import DuplicateKeyError

from services.ingestion_service import IngestionService


class FakeCollection:
    def __init__(self):
        self._ids = set()

    def insert_one(self, doc):
        if doc["event_id"] in self._ids:
            raise DuplicateKeyError("duplicate event_id")
        self._ids.add(doc["event_id"])


class FakeDB:
    def __init__(self):
        self.earthquakes = FakeCollection()

    def __getitem__(self, _name):
        return self.earthquakes


class FakeUsgsClient:
    def __init__(self, features):
        self._features = features

    def fetch_features(self):
        return self._features


class FakeProcessingService:
    def __init__(self):
        self.calls = []

    def update_metrics(self, events):
        self.calls.append(events)


def _feature(event_id, mag=3.0):
    return {
        "id": event_id,
        "properties": {"mag": mag, "place": "Somewhere", "time": 1718610000000},
        "geometry": {"coordinates": [-120.0, 35.0, 10.0]},
    }


def test_run_once_ingests_new_events_and_updates_metrics():
    processing_service = FakeProcessingService()
    service = IngestionService(
        db=FakeDB(),
        usgs_client=FakeUsgsClient([_feature("a"), _feature("b")]),
        processing_service=processing_service,
    )

    inserted = service.run_once()

    assert inserted == 2
    assert len(processing_service.calls) == 1
    assert len(processing_service.calls[0]) == 2


def test_run_once_skips_duplicates_on_second_cycle():
    processing_service = FakeProcessingService()
    service = IngestionService(
        db=FakeDB(),
        usgs_client=FakeUsgsClient([_feature("a")]),
        processing_service=processing_service,
    )

    service.run_once()
    inserted_second_cycle = service.run_once()

    assert inserted_second_cycle == 0
    assert len(processing_service.calls) == 1


def test_run_once_skips_features_without_magnitude():
    processing_service = FakeProcessingService()
    feature_without_mag = _feature("c")
    feature_without_mag["properties"]["mag"] = None
    service = IngestionService(
        db=FakeDB(),
        usgs_client=FakeUsgsClient([feature_without_mag]),
        processing_service=processing_service,
    )

    inserted = service.run_once()

    assert inserted == 0
    assert processing_service.calls == []
