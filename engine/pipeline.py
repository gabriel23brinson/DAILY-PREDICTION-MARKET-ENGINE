from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from .contracts import ContractKind
from .eligibility import evaluate_market
from .stations import extract_station_target
from .weather import NWSClient
from .weather_model import build_temperature_input
from .crypto_model import CoinbasePublicClient, build_crypto_input, product_for_title
from .research import WeatherResearchAdapter, CryptoResearchAdapter, research_with_adapter, ResearchResult
from .ledger import Ledger

@dataclass(frozen=True)
class PipelineResult:
    status: str
    reason: str
    research: ResearchResult | None = None
    prediction_id: int | None = None

def _yes_ask(market: dict[str,Any]) -> Decimal | None:
    ask=market.get("yes_ask_dollars")
    if ask is None and market.get("yes_ask") is not None:
        return Decimal(str(market["yes_ask"]))/Decimal("100")
    return Decimal(str(ask)) if ask is not None else None

def research_market(market: dict[str,Any], *, nws_user_agent: str="prediction-market-research/0.1",
                    persist: bool=False, ledger: Ledger | None=None,
                    coinbase: CoinbasePublicClient | None=None) -> PipelineResult:
    e=evaluate_market(market)
    if not e.eligible: return PipelineResult("PASS",e.reason)
    ask=_yes_ask(market)
    evidence=None

    if e.contract.kind is ContractKind.CRYPTO_PRICE:
        product=product_for_title(" ".join(str(market.get(k) or "") for k in ("title","subtitle","yes_sub_title")))
        if product is None: return PipelineResult("PASS","unsupported crypto asset")
        cb=coinbase or CoinbasePublicClient()
        crypto=build_crypto_input(ticker=e.contract.ticker,product_id=product,
                                  spot_payload=cb.ticker(product),candles_payload=cb.candles(product),
                                  retrieved_at=datetime.now(timezone.utc))
        adapter=CryptoResearchAdapter(crypto=crypto,floor=e.contract.floor_strike,cap=e.contract.cap_strike)
        evidence=crypto.evidence
    else:
        target=extract_station_target(market)
        if target.latitude is None or target.longitude is None:
            return PipelineResult("PASS",target.reason or "missing coordinates")
        nws=NWSClient(nws_user_agent)
        payload=nws.evidence_for_point(target.latitude,target.longitude)
        weather=build_temperature_input(ticker=e.contract.ticker,nws_payload=payload,retrieved_at=datetime.now(timezone.utc))
        adapter=WeatherResearchAdapter(weather=weather,floor=e.contract.floor_strike,cap=e.contract.cap_strike)
        evidence=weather.evidence

    r=research_with_adapter(adapter=adapter,ticker=e.contract.ticker,yes_ask=ask)
    prediction_id=None
    if persist:
        model_name=f"{adapter.family}_baseline"
        prediction_id=(ledger or Ledger()).record(market=market,result=r,evidence=evidence,model_name=model_name)
    return PipelineResult(r.edge.decision,r.edge.reason,r,prediction_id)
