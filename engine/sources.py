from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class SourceRole(str, Enum):
    SETTLEMENT = "settlement"
    PRIMARY = "primary"
    INDEPENDENT = "independent"
    HISTORICAL = "historical"
    MARKET = "market"

@dataclass(frozen=True)
class SourceSpec:
    name: str
    role: SourceRole
    authoritative_for: tuple[str, ...]
    notes: str

WEATHER_SOURCES = (
    SourceSpec("Kalshi contract rules", SourceRole.SETTLEMENT, ("contract", "settlement"), "Exact contract language and named settlement source."),
    SourceSpec("NWS API", SourceRole.PRIMARY, ("forecast", "hourly", "grid", "observations"), "Primary US weather forecast/observation feed."),
    SourceSpec("NOAA/NCEI", SourceRole.HISTORICAL, ("climate_history", "quality_controlled_observations"), "Historical climate and final QC layer."),
    SourceSpec("NDFD", SourceRole.INDEPENDENT, ("digital_forecast",), "Additional NWS digital forecast representation; correlated with NWS and must not be double-counted as independent."),
)
