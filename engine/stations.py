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

ICAO=re.compile(r"\bK[A-Z]{3}\b", re.IGNORECASE)
COORD=re.compile(r"(-?\d{1,2}(?:\.\d+)?)\s*[,°]\s*(-?\d{1,3}(?:\.\d+)?)")

# Verified series-location mappings used only when contract text omits coordinates.\nSERIES_COORDS={\n    "KXTEMPMIAH": (25.7959,-80.2870),\n}\n\ndef extract_station_target(market: dict[str,Any]) -> StationTarget:
    text=" ".join(str(market.get(k) or "") for k in ("rules_primary","rules_secondary","title","subtitle"))
    station=ICAO.search(text)
    coord=COORD.search(text)
    ticker=str(market.get("ticker") or "").upper()
    series=next((key for key in SERIES_COORDS if ticker.startswith(key)),None)
    lat=lon=None
    if coord:
        lat,lon=float(coord.group(1)),float(coord.group(2))
        if not (-90<=lat<=90 and -180<=lon<=180): lat=lon=None
    if lat is None and series:
        lat,lon=SERIES_COORDS[series]
    if station or lat is not None:
        return StationTarget(station.group(0).upper() if station else None,lat,lon,"high",None)
    return StationTarget(None,None,None,"fail","station/coordinates not identified from contract")
