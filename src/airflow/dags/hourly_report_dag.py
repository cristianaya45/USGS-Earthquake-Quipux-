from datetime import timedelta

import pendulum
from airflow.decorators import dag, task

from database.mongodb import get_database
from services.reporting_service import ReportingService
from utils.time_utils import previous_hour_start


@dag(
    dag_id="hourly_earthquake_report",
    description="Genera el reporte consolidado de la última hora de sismos",
    schedule="@hourly",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["usgs", "earthquake"],
)
def hourly_earthquake_report():
    @task
    def generate_report() -> list[dict]:
        # Regenera (upsert) las últimas 2 horas, no solo la anterior: el feed del
        # USGS a veces reporta eventos con algunos minutos de retraso respecto a
        # su event_time real, así que un evento de la hora N puede no estar
        # todavía en Mongo cuando se genera su reporte a las N+1. Al recalcular
        # también N-1 en la siguiente corrida, esos eventos tardíos quedan
        # reflejados sin necesitar backfill manual.
        db = get_database()
        service = ReportingService(db)
        current_hour_start = previous_hour_start()
        hours = (current_hour_start, current_hour_start - timedelta(hours=1))
        return [
            {"report_date": report["report_date"].isoformat(), "total_events": report["total_events"]}
            for report in (service.generate_hourly_report(hour_start) for hour_start in hours)
        ]

    generate_report()


hourly_earthquake_report()
