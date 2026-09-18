from datetime import timedelta

from services.processing_service import ProcessingService


def test_build_distribution_buckets_by_magnitude_range():
    distribution = ProcessingService._build_distribution([1.0, 2.5, 4.5, 5.5, 6.5, 7.5, 8.5])
    assert distribution == {
        "micro": 1,
        "minor": 1,
        "light": 1,
        "moderate": 1,
        "strong": 1,
        "major": 1,
        "great": 1,
    }


def test_window_bounds_returns_one_hour_span():
    start, end = ProcessingService._window_bounds("2026-06-17T10")
    assert end - start == timedelta(hours=1)
    assert start.hour == 10
