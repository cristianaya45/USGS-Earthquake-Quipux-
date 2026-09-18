from services.reporting_service import ReportingService


def test_top_locations_returns_most_common_first():
    locations = ["California", "California", "Alaska", "Chile", "Chile", "Chile"]
    assert ReportingService._top_locations(locations, top_n=2) == ["Chile", "California"]


def test_top_locations_handles_empty_list():
    assert ReportingService._top_locations([]) == []
