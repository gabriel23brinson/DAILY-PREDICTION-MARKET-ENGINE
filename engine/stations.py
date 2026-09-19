from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Any

@dataclass(frozen=True)
class StationTarget:
    station_id: str | None
    latitude: float | None
    longitude: float | None
    confidence: str
    reason: str | None = None

ICAO=re.compile(r"\bK[A-Z]{3}\b")
COORD=re.compile(r"(-?\d{1,2}(?:\.\d+)?)\s*[,°]\s*(-?\d{1,3}(?:\.\d+)?)")

def extract_station_target(market: dict[str,Any]) -> StationTarget:
    text=" ".join(str(market.get(k) or "") for k in ("rules_primary","rules_secondary","title","subtitle"))
    station=ICAO.search(text)
    coord=COORD.search(text)
    lat=lon=None
    if coord:
        lat,lon=float(coord.group(1)),float(coord.group(2))
        if not (-90<=lat<=90 and -180<=lon<=180): lat=lon=None
    if station or lat is not None:
        return StationTarget(station.group(0) if station else None,lat,lon,"high",None)
    return StationTarget(None,None,None,"fail","station/coordinates not identified from contract")
