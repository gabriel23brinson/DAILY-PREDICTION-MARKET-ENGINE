from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from .edge import EdgeResult, evaluate_edge
from .probability import ProbabilityEstimate, weather_interval_estimate
from .weather_model import WeatherModelInput

@dataclass(frozen=True)
class ResearchResult:
    ticker: str
    probability: ProbabilityEstimate
    edge: EdgeResult
    diagnostics: dict

class CategoryResearchAdapter(Protocol):
    """Category-specific research behind a category-agnostic orchestration boundary."""
    family: str

    def research(self, *, ticker: str, yes_ask: Decimal | None) -> ResearchResult:
        ...

def research_with_adapter(*, adapter: CategoryResearchAdapter, ticker: str,
                          yes_ask: Decimal | None) -> ResearchResult:
    result=adapter.research(ticker=ticker,yes_ask=yes_ask)
    if result.ticker != ticker:
        raise ValueError("category adapter returned mismatched ticker")
    return result

def research_weather_contract(*, ticker: str, weather: WeatherModelInput, floor: float | None, cap: float | None,
                              yes_ask: Decimal | None, estimated_cost: Decimal=Decimal("0"),
                              minimum_net_edge: Decimal=Decimal("0.05")) -> ResearchResult:
    if weather.evidence.critical_failure():
        raise ValueError(weather.evidence.critical_failure())
    p=weather_interval_estimate(weather.mean_f,weather.sigma_f,floor,cap)
    edge=evaluate_edge(side="YES",model_probability=Decimal(str(p.probability)),executable_price=yes_ask,
                       estimated_cost=estimated_cost,minimum_net_edge=minimum_net_edge)
    return ResearchResult(ticker,p,edge,weather.diagnostics)
