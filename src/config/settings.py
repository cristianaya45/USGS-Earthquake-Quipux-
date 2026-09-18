from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongo_uri: str = "mongodb://mongo:27017"
    mongo_db: str = "usgs_earthquake"

    usgs_api_url: str = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    ingestion_interval_seconds: int = 180

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
