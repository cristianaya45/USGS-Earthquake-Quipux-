EARTHQUAKES_COLLECTION = "earthquakes"
METRICS_COLLECTION = "metrics"
HOURLY_REPORTS_COLLECTION = "hourly_reports"

HOUR_WINDOW_FORMAT = "%Y-%m-%dT%H"

# Rangos de magnitud basados en la clasificación estándar del USGS.
MAGNITUDE_RANGES = [
    ("micro", float("-inf"), 2.0),
    ("minor", 2.0, 4.0),
    ("light", 4.0, 5.0),
    ("moderate", 5.0, 6.0),
    ("strong", 6.0, 7.0),
    ("major", 7.0, 8.0),
    ("great", 8.0, float("inf")),
]
