from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from .kalshi import KalshiPublicClient

@dataclass(frozen=True)
class LiveMarketSnapshot:
    ticker: str
    captured_at: datetime
    yes_bid: Decimal | None
    yes_ask: Decimal | None
    no_bid: Decimal | None
    no_ask: Decimal | None
    volume: Decimal | None
    open_interest: Decimal | None
    orderbook: dict[str, Any]

def _d(v: Any) -> Decimal | None:
    if v is None or v == "": return None
    return Decimal(str(v))

def capture_live_market(ticker: str, client: KalshiPublicClient | None = None) -> LiveMarketSnapshot:
    client = client or KalshiPublicClient()
    wrapper = client.get_market(ticker)
    m = wrapper.get("market", wrapper)
    book = client.get_orderbook(ticker)
    return LiveMarketSnapshot(
        ticker=ticker,
        captured_at=datetime.now(timezone.utc),
        yes_bid=_d(m.get("yes_bid_dollars") or m.get("yes_bid")),
        yes_ask=_d(m.get("yes_ask_dollars") or m.get("yes_ask")),
        no_bid=_d(m.get("no_bid_dollars") or m.get("no_bid")),
        no_ask=_d(m.get("no_ask_dollars") or m.get("no_ask")),
        volume=_d(m.get("volume_fp") or m.get("volume")),
        open_interest=_d(m.get("open_interest_fp") or m.get("open_interest")),
        orderbook=book,
    )
