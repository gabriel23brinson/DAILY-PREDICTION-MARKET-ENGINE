from __future__ import annotations
from typing import Any
import httpx

NWS_BASE = "https://api.weather.gov"

class NWSClient:
    def __init__(self, user_agent: str, timeout: float = 15.0) -> None:
        self.client = httpx.Client(
            base_url=NWS_BASE,
            timeout=timeout,
            headers={"User-Agent": user_agent, "Accept": "application/geo+json"},
        )

    def point(self, latitude: float, longitude: float) -> dict[str, Any]:
        r = self.client.get(f"/points/{latitude:.4f},{longitude:.4f}")
        r.raise_for_status()
        return r.json()

    def get_url(self, url: str) -> dict[str, Any]:
        r = self.client.get(url)
        r.raise_for_status()
        return r.json()

    def evidence_for_point(self, latitude: float, longitude: float) -> dict[str, Any]:
        point = self.point(latitude, longitude)
        props = point["properties"]
        return {
            "point": point,
            "forecast": self.get_url(props["forecast"]),
            "hourly": self.get_url(props["forecastHourly"]),
            "grid": self.get_url(props["forecastGridData"]),
            "stations_url": props.get("observationStations"),
        }
