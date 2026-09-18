# Diagrama de arquitectura

```mermaid
flowchart LR
    USGS["USGS Earthquake API\n(GeoJSON feed)"]

    subgraph Docker Compose
        ING["Servicio de Ingesta\n(loop cada 3 min)"]
        API["API REST\n(FastAPI)"]
        MONGO[("MongoDB\nearthquakes / metrics / hourly_reports")]

        subgraph Airflow
            SCHED["Scheduler"]
            WEB["Webserver"]
            PG[("Postgres\n(metadata Airflow)")]
        end
    end

    CLIENT["Cliente / Postman"]

    USGS -- "GET cada 3 min" --> ING
    ING -- "insert_one (dedupe por event_id)" --> MONGO
    ING -- "recalcula métricas de la ventana horaria" --> MONGO

    CLIENT -- "GET /earthquakes /metrics /reports" --> API
    API -- "find / aggregate" --> MONGO

    SCHED -- "DAG hourly_earthquake_report\n(cada hora)" --> MONGO
    SCHED --- PG
    WEB --- PG
```

## Flujo

1. El **servicio de ingesta** consulta el feed del USGS cada 3 minutos,
   transforma cada feature a un modelo interno (Pydantic), descarta
   duplicados (`event_id` único) y guarda los eventos nuevos en
   `earthquakes`.
2. Tras cada ciclo con eventos nuevos, recalcula las **métricas** de la(s)
   ventana(s) horaria(s) afectadas (conteo, promedio, máximo, distribución
   por rango de magnitud) y las guarda (upsert) en `metrics`.
3. La **API REST** (FastAPI) solo lee de MongoDB: expone `/earthquakes`,
   `/metrics` y `/reports` con filtros, orden y paginación.
4. **Airflow** ejecuta cada hora el DAG `hourly_earthquake_report`, que lee
   los eventos de la hora anterior y genera/actualiza el reporte consolidado
   en `hourly_reports` (top ubicaciones, promedio y máximo de magnitud).
5. Airflow usa su propia base **Postgres** para metadata (scheduler, DAG
   runs), completamente separada de los datos de la aplicación en MongoDB.
