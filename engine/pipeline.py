from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from .eligibility import evaluate_market
from .stations import extract_station_target
from .weather import NWSClient
from .weather_model import build_temperature_input
from .research import WeatherResearchAdapter, research_with_adapter, ResearchResult
from .ledger import Ledger

@dataclass(frozen=True)
class PipelineResult:
    status: str
    reason: str
    research: ResearchResult | None = None
    prediction_id: int | None = None

def research_market(market: dict[str,Any], *, nws_user_agent: str, persist: bool=False,
                    ledger: Ledger | None=None) -> PipelineResult:
    e=evaluate_market(market)
    if not e.eligible: return PipelineResult("PASS",e.reason)
    target=extract_station_target(market)
    if target.latitude is None or target.longitude is None:
        return PipelineResult("PASS",target.reason or "missing coordinates")
    nws=NWSClient(nws_user_agent)
    payload=nws.evidence_for_point(target.latitude,target.longitude)
    weather=build_temperature_input(ticker=e.contract.ticker,nws_payload=payload,retrieved_at=datetime.now(timezone.utc))
    ask=market.get("yes_ask_dollars")
    if ask is None and market.get("yes_ask") is not None:
        ask=Decimal(str(market["yes_ask"]))/Decimal("100")
    elif ask is not None:
        ask=Decimal(str(ask))
    adapter=WeatherResearchAdapter(weather=weather,floor=e.contract.floor_strike,cap=e.contract.cap_strike)
    r=research_with_adapter(adapter=adapter,ticker=e.contract.ticker,yes_ask=ask)
    prediction_id=None
    if persist:
        prediction_id=(ledger or Ledger()).record(market=market,result=r,evidence=weather.evidence)
    return PipelineResult(r.edge.decision,r.edge.reason,r,prediction_id)
