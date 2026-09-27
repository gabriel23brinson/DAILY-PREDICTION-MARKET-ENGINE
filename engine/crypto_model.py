from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from math import log, sqrt
from statistics import pstdev
from typing import Any
import httpx
from .evidence import EvidenceBundle, EvidenceItem, SourceTier

COINBASE_BASE_URL="https://api.exchange.coinbase.com"

@dataclass(frozen=True)
class CryptoModelInput:
    spot: float
    sigma_log: float
    evidence: EvidenceBundle
    diagnostics: dict[str, Any]

class CoinbasePublicClient:
    """Read-only Coinbase public market-data client."""
    def __init__(self, timeout: float=15.0) -> None:
        self.client=httpx.Client(base_url=COINBASE_BASE_URL,timeout=timeout,headers={"User-Agent":"prediction-market-research/0.1"})
    def ticker(self, product_id: str) -> dict[str,Any]:
        r=self.client.get(f"/products/{product_id}/ticker"); r.raise_for_status(); return r.json()
    def candles(self, product_id: str, *, granularity: int=300) -> list[list[Any]]:
        r=self.client.get(f"/products/{product_id}/candles",params={"granularity":granularity}); r.raise_for_status(); return r.json()

def product_for_title(title: str) -> str | None:
    low=title.lower()
    if "bitcoin" in low or "btc" in low.split(): return "BTC-USD"
    if "ethereum" in low or "eth" in low.split(): return "ETH-USD"
    return None

def build_crypto_input(*, ticker: str, product_id: str, spot_payload: dict[str,Any],
                       candles_payload: list[list[Any]], retrieved_at: datetime | None=None) -> CryptoModelInput:
    retrieved_at=retrieved_at or datetime.now(timezone.utc)
    spot=float(spot_payload["price"])
    closes=[float(row[4]) for row in candles_payload if len(row)>4 and float(row[4])>0]
    if spot<=0: raise ValueError("invalid critical crypto spot price")
    if len(closes)<3: raise ValueError("missing critical crypto price history")
    returns=[log(closes[i]/closes[i+1]) for i in range(len(closes)-1) if closes[i+1]>0]
    sigma=max(pstdev(returns)*sqrt(12),0.001)
    evidence=EvidenceBundle(market_ticker=ticker,items=[
        EvidenceItem(provider="Coinbase",source_tier=SourceTier.PRIMARY,endpoint=f"{product_id}/ticker",retrieved_at=retrieved_at,value=spot_payload,units="USD",critical=True),
        EvidenceItem(provider="Coinbase",source_tier=SourceTier.HISTORICAL,endpoint=f"{product_id}/candles",retrieved_at=retrieved_at,value=candles_payload,units="USD",critical=True),
    ])
    return CryptoModelInput(spot,sigma,evidence,{"product_id":product_id,"spot":spot,"sigma_log":sigma,"method":"coinbase_intraday_v0"})
