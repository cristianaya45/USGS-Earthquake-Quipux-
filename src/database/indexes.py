from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database

from config.constants import EARTHQUAKES_COLLECTION, HOURLY_REPORTS_COLLECTION, METRICS_COLLECTION


def ensure_indexes(db: Database) -> None:
    earthquakes = db[EARTHQUAKES_COLLECTION]
    # event_id único: red de seguridad a nivel de base de datos contra duplicados,
    # complementaria a la verificación que hace el servicio de ingesta.
    earthquakes.create_index([("event_id", ASCENDING)], unique=True, name="uniq_event_id")
    # event_time desc: soporta el orden por defecto (más recientes primero) y
    # los filtros por rango de fecha usados en /earthquakes y en los reportes.
    earthquakes.create_index([("event_time", DESCENDING)], name="event_time_desc")
    # magnitude desc: soporta filtro/orden por magnitud en /earthquakes.
    earthquakes.create_index([("magnitude", DESCENDING)], name="magnitude_desc")
    # location asc: soporta búsquedas por ubicación (regex con prefijo/anclaje).
    earthquakes.create_index([("location", ASCENDING)], name="location_asc")

    metrics = db[METRICS_COLLECTION]
    # window único: es la clave natural del documento, permite upsert directo
    # al recalcular métricas de una ventana horaria.
    metrics.create_index([("window", ASCENDING)], unique=True, name="uniq_window")

    hourly_reports = db[HOURLY_REPORTS_COLLECTION]
    hourly_reports.create_index([("report_date", DESCENDING)], unique=True, name="uniq_report_date")
