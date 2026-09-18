# USGS Earthquake — Plataforma de eventos sísmicos en tiempo real

Prueba técnica para Quipux. Ingiere el feed público de terremotos del USGS,
lo procesa en (casi) tiempo real, lo persiste en MongoDB y expone métricas y
reportes a través de una API FastAPI y un DAG de Airflow.

## Arquitectura

```
├── src/
│   ├── config/        # settings (pydantic-settings), logging estructurado, constantes
│   ├── metadata/       # validadores de dominio y JSON Schema de MongoDB
│   ├── models/         # modelos Pydantic (Earthquake, Metric, Report)
│   ├── database/       # conexión Mongo (singleton) e índices
│   ├── clients/        # cliente HTTP del feed USGS
│   ├── services/       # ingesta, procesamiento de métricas, consultas, reportes
│   ├── api/             # FastAPI: rutas, dependencias, serialización
│   └── airflow/dags/    # DAG horario de reportes consolidados
├── deploy/              # Dockerfiles (api, ingestion, airflow)
├── postman/             # colección Postman
├── docs/                # diagrama de arquitectura
├── main.py              # entrypoint del servicio de ingesta (loop cada N segundos)
└── docker-compose.yml
```

**Separación de responsabilidades:** `clients` solo sabe hablar con el USGS,
`services` contiene la lógica de negocio (ingesta, métricas, reportes) y no
conoce HTTP ni FastAPI, `api` es una capa delgada que traduce HTTP ↔ servicios,
y `database` es el único lugar que sabe cómo se conecta a Mongo. Esto permite
que el mismo código de `services` lo usen tanto el proceso de ingesta como el
DAG de Airflow sin duplicación.

## Decisiones de diseño

- **Conexión a Mongo (pymongo, síncrono, en todos los servicios).** FastAPI,
  el loop de ingesta y las tasks de Airflow comparten el mismo cliente
  `pymongo` singleton (`database/mongodb.py`, `lru_cache`). Se optó por
  síncrono en vez de `motor`/async porque Airflow ejecuta tasks síncronas y
  así se evita mantener dos drivers Mongo distintos; FastAPI ejecuta las
  rutas `def` (no `async def`) en su threadpool interno, así que no hay
  bloqueo del event loop.
- **Deduplicación en dos capas.** El servicio de ingesta intenta un
  `insert_one` y captura `DuplicateKeyError`; el índice único sobre
  `event_id` es la garantía real a nivel de base de datos (la app podría
  tener una condición de carrera si corrieran varias réplicas de ingesta).
- **Métricas recalculadas por agregación, no incrementadas.** Al recibir
  eventos nuevos, `ProcessingService` vuelve a agregar *toda* la ventana
  horaria afectada (count/avg/max/distribución) en vez de incrementar
  contadores. Es más simple, evita errores de redondeo acumulados y el
  volumen por hora (decenas de eventos) hace que el costo sea despreciable.
- **Índices** (`database/indexes.py`): `event_id` único (dedupe), `event_time`
  descendente (orden por defecto y filtros de rango en `/earthquakes` y
  reportes), `magnitude` descendente (filtro/orden), `location` (búsqueda),
  y `window`/`report_date` únicos en `metrics`/`hourly_reports` (son la
  clave natural de esos documentos y el destino de los `upsert`).
- **Airflow con Postgres propio.** Se usa `LocalExecutor` con una base
  Postgres dedicada solo a metadata de Airflow (no a datos de la aplicación,
  que viven en Mongo). Es el patrón estándar de Airflow en Docker; usar
  `SequentialExecutor`+SQLite sería más liviano pero no es una práctica que
  se sostenga si el DAG creciera.
- **Sin credenciales hardcodeadas.** Todo viene de variables de entorno con
  defaults de desarrollo definidos en `docker-compose.yml` (`${VAR:-default}`)
  y documentados en `.env.example`. Para un entorno real, `.env` no se
  versiona y los defaults deben sobrescribirse.

## Cómo ejecutar

```bash
docker compose up --build
```

Servicios expuestos:

| Servicio | URL |
|---|---|
| API REST | http://localhost:8000 (docs interactivas en `/docs`) |
| Airflow  | http://localhost:8080 (usuario/clave: `admin` / `admin` por defecto) |
| MongoDB  | localhost:27017 |

El servicio de ingesta no expone puertos; corre en loop consultando el feed
del USGS cada `INGESTION_INTERVAL_SECONDS` (180s por defecto) y escribe en
sus logs (JSON estructurado) cada ciclo.

### Variables de entorno

Ver [.env.example](.env.example). Copiar a `.env` para sobrescribir cualquier
default.

### Ejecutar localmente sin Docker

```bash
pip install -r requirements-api.txt
$env:PYTHONPATH = "src"        # PowerShell
uvicorn api.main:app --reload  # API
python main.py                 # servicio de ingesta (en otra terminal)
```

Requiere una instancia de MongoDB accesible en `MONGO_URI`.

## Endpoints

- `GET /earthquakes` — filtros `min_magnitude`, `max_magnitude`, `location`;
  orden por `sort_by` (`event_time`|`magnitude`) y `order` (`asc`|`desc`);
  paginación `page`/`page_size`.
- `GET /metrics` — filtro opcional por `window` (`YYYY-MM-DDTHH`), paginado.
- `GET /reports` — reportes horarios generados por el DAG de Airflow, paginado.
- `GET /health` — healthcheck.

Colección Postman lista en [postman/USGS-Earthquake.postman_collection.json](postman/USGS-Earthquake.postman_collection.json).

## DAG de Airflow

`hourly_earthquake_report` corre cada hora y regenera (upsert) el reporte
consolidado de las **últimas 2 horas** (no solo la anterior) en
`hourly_reports`. Se regeneran 2 en vez de 1 porque el feed del USGS a veces
reporta eventos con algunos minutos de retraso respecto a su `event_time`
real: un evento de la hora N puede no estar todavía en Mongo cuando se genera
el reporte de esa hora a las N+1. Al recalcular también N-1 en cada corrida,
esos eventos tardíos quedan reflejados en la siguiente ejecución sin
necesitar backfill manual. El DAG está en `src/airflow/dags/`, montado como
volumen en los contenedores de Airflow (no requiere rebuild de la imagen al
modificarlo).

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Suite de pruebas unitarias (sin Docker/Mongo) sobre la lógica de negocio:
validadores de dominio, transformación de features del USGS, bucketing de
magnitud, `top_locations` de reportes y el flujo de deduplicación de ingesta.
