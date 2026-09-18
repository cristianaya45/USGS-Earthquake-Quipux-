import logging

import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)


class UsgsClient:
    def __init__(self, api_url: str | None = None, timeout: float = 10.0):
        self._api_url = api_url or get_settings().usgs_api_url
        self._timeout = timeout

    def fetch_features(self) -> list[dict]:
        response = requests.get(self._api_url, timeout=self._timeout)
        response.raise_for_status()
        features = response.json().get("features", [])
        logger.info("usgs_fetch_success", extra={"feature_count": len(features)})
        return features
