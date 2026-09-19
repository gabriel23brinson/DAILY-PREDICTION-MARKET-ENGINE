from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from statistics import mean, pstdev
from typing import Any
from .evidence import EvidenceBundle, EvidenceItem, SourceTier

@dataclass(frozen=True)
class WeatherModelInput:
    mean_f: float
    sigma_f: float
    evidence: EvidenceBundle
    diagnostics: dict[str, Any]

def c_to_f(c: float) -> float:
    return c * 9.0 / 5.0 + 32.0

def _values(grid: dict[str, Any], key: str) -> list[float]:
    values=((grid.get("properties") or {}).get(key) or {}).get("values") or []
    out=[]
    for row in values:
        v=row.get("value")
        if isinstance(v,(int,float)): out.append(float(v))
    return out

def build_temperature_input(*, ticker: str, nws_payload: dict[str, Any], retrieved_at: datetime) -> WeatherModelInput:
    grid=nws_payload.get("grid") or {}
    hourly=nws_payload.get("hourly") or {}
    grid_c=_values(grid,"temperature")
    hourly_periods=(hourly.get("properties") or {}).get("periods") or []
    hourly_f=[float(p["temperature"]) for p in hourly_periods if isinstance(p.get("temperature"),(int,float))]
    if not grid_c:
        raise ValueError("missing critical NWS grid temperature forecast")
    if not hourly_f:
        raise ValueError("missing critical NWS hourly temperature forecast")
    candidates=[c_to_f(mean(grid_c[:24])), mean(hourly_f[:24])]
    center=mean(candidates)
    disagreement=pstdev(candidates) if len(candidates)>1 else 0.0
    sigma=max(2.0, disagreement, pstdev(hourly_f[:24]) if len(hourly_f[:24])>1 else 0.0)
    evidence=EvidenceBundle(market_ticker=ticker,items=[
        EvidenceItem(provider="NWS API",source_tier=SourceTier.PRIMARY,endpoint="forecastGridData",retrieved_at=retrieved_at,value={"temperature_c":grid_c[:24]},units="C",critical=True),
        EvidenceItem(provider="NWS API",source_tier=SourceTier.PRIMARY,endpoint="forecastHourly",retrieved_at=retrieved_at,value={"temperature_f":hourly_f[:24]},units="F",critical=True),
    ])
    return WeatherModelInput(center,sigma,evidence,{"candidate_means_f":candidates,"source_disagreement_f":disagreement,"method":"nws_baseline_v0"})
