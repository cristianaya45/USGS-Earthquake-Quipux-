# Esquemas de validación a nivel de MongoDB (defensa en profundidad además
# de la validación de Pydantic en la capa de aplicación).

EARTHQUAKE_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["event_id", "magnitude", "location", "latitude", "longitude", "depth", "event_time"],
        "properties": {
            "event_id": {"bsonType": "string"},
            "magnitude": {"bsonType": "double"},
            "location": {"bsonType": "string"},
            "latitude": {"bsonType": "double"},
            "longitude": {"bsonType": "double"},
            "depth": {"bsonType": "double"},
            "event_time": {"bsonType": "date"},
        },
    }
}

METRICS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["window", "earthquake_count", "avg_magnitude", "max_magnitude"],
        "properties": {
            "window": {"bsonType": "string"},
            "earthquake_count": {"bsonType": "int"},
            "avg_magnitude": {"bsonType": "double"},
            "max_magnitude": {"bsonType": "double"},
            "magnitude_distribution": {"bsonType": "object"},
        },
    }
}

HOURLY_REPORTS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["report_date", "total_events", "average_magnitude", "max_magnitude"],
        "properties": {
            "report_date": {"bsonType": "date"},
            "total_events": {"bsonType": "int"},
            "average_magnitude": {"bsonType": "double"},
            "max_magnitude": {"bsonType": "double"},
            "top_locations": {"bsonType": "array"},
        },
    }
}
