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
    def generate_report() -> dict:
        db = get_database()
        service = ReportingService(db)
        report = service.generate_hourly_report(previous_hour_start())
        return {"report_date": report["report_date"].isoformat(), "total_events": report["total_events"]}

    generate_report()


hourly_earthquake_report()
