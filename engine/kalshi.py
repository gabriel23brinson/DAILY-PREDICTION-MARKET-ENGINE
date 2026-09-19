from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import httpx

BASE_URL = "https://external-api.kalshi.com/trade-api/v2"

class KalshiPublicClient:
    """Read-only live Kalshi market-data client. No order placement methods."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.client = httpx.Client(base_url=BASE_URL, timeout=timeout)

    def get_markets(self, *, limit: int = 1000, cursor: str | None = None, status: str = "open", series_ticker: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "status": status}
        if cursor: params["cursor"] = cursor
        if series_ticker: params["series_ticker"] = series_ticker
        r = self.client.get("/markets", params=params); r.raise_for_status(); return r.json()

    def get_market(self, ticker: str) -> dict[str, Any]:
        r = self.client.get(f"/markets/{ticker}"); r.raise_for_status(); return r.json()

    def get_event(self, event_ticker: str) -> dict[str, Any]:
        r = self.client.get(f"/events/{event_ticker}"); r.raise_for_status(); return r.json()

    def get_series(self, series_ticker: str) -> dict[str, Any]:
        r = self.client.get(f"/series/{series_ticker}"); r.raise_for_status(); return r.json()

    def get_orderbook(self, ticker: str, depth: int | None = None) -> dict[str, Any]:
        params = {"depth": depth} if depth is not None else None
        r = self.client.get(f"/markets/{ticker}/orderbook", params=params); r.raise_for_status(); return r.json()

def _parse_dt(value: str | None) -> datetime | None:
    if not value: return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def outcome_is_same_utc_day(market: dict[str, Any], now: datetime | None = None) -> bool:
    """Conservative discovery filter only; semantic eligibility applies contract timezone rules."""
    now = now or datetime.now(timezone.utc)
    expiry = _parse_dt(market.get("expected_expiration_time") or market.get("expiration_time") or market.get("close_time"))
    return bool(expiry and expiry.astimezone(timezone.utc).date() == now.astimezone(timezone.utc).date())
