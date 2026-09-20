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

class UnsupportedCategoryError(ValueError):
    pass

class CategoryResearchAdapter(Protocol):
    """Category-specific research behind a category-agnostic orchestration boundary."""
    family: str

    def research(self, *, ticker: str, yes_ask: Decimal | None) -> ResearchResult:
        ...

def research_with_adapter(*, adapter: CategoryResearchAdapter, ticker: str,
                          yes_ask: Decimal | None) -> ResearchResult:
    family=getattr(adapter,"family",None)
    if not isinstance(family,str) or not family.strip():
        raise UnsupportedCategoryError("category adapter missing model family")
    result=adapter.research(ticker=ticker,yes_ask=yes_ask)
    if result.ticker != ticker:
        raise ValueError("category adapter returned mismatched ticker")
    return result

@dataclass(frozen=True)
class WeatherResearchAdapter:
    weather: WeatherModelInput
    floor: float | None
    cap: float | None
    estimated_cost: Decimal=Decimal("0")
    minimum_net_edge: Decimal=Decimal("0.05")
    family: str="weather"

    def research(self, *, ticker: str, yes_ask: Decimal | None) -> ResearchResult:
        if self.weather.evidence.market_ticker != ticker:
            raise ValueError("category adapter input has mismatched ticker")
        return research_weather_contract(
            ticker=ticker, weather=self.weather, floor=self.floor, cap=self.cap,
            yes_ask=yes_ask, estimated_cost=self.estimated_cost,
            minimum_net_edge=self.minimum_net_edge,
        )

def research_weather_contract(*, ticker: str, weather: WeatherModelInput, floor: float | None, cap: float | None,
                              yes_ask: Decimal | None, estimated_cost: Decimal=Decimal("0"),
                              minimum_net_edge: Decimal=Decimal("0.05")) -> ResearchResult:
    if weather.evidence.critical_failure():
        raise ValueError(weather.evidence.critical_failure())
    p=weather_interval_estimate(weather.mean_f,weather.sigma_f,floor,cap)
    edge=evaluate_edge(side="YES",model_probability=Decimal(str(p.probability)),executable_price=yes_ask,
                       estimated_cost=estimated_cost,minimum_net_edge=minimum_net_edge)
    return ResearchResult(ticker,p,edge,weather.diagnostics)
