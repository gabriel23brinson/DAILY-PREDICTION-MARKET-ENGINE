from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from .edge import EdgeResult, evaluate_edge
from .probability import ProbabilityEstimate, weather_interval_estimate
from .weather_model import WeatherModelInput

@dataclass(frozen=True)
class ResearchResult:
    ticker: str
    probability: ProbabilityEstimate
    edge: EdgeResult
    diagnostics: dict

def research_weather_contract(*, ticker: str, weather: WeatherModelInput, floor: float | None, cap: float | None,
                              yes_ask: Decimal | None, estimated_cost: Decimal=Decimal("0"),
                              minimum_net_edge: Decimal=Decimal("0.05")) -> ResearchResult:
    if weather.evidence.critical_failure():
        raise ValueError(weather.evidence.critical_failure())
    p=weather_interval_estimate(weather.mean_f,weather.sigma_f,floor,cap)
    edge=evaluate_edge(side="YES",model_probability=Decimal(str(p.probability)),executable_price=yes_ask,
                       estimated_cost=estimated_cost,minimum_net_edge=minimum_net_edge)
    return ResearchResult(ticker,p,edge,weather.diagnostics)
