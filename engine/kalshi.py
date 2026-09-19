from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import httpx

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

class KalshiPublicClient:
    """Read-only public market-data client. V0.1 intentionally has no order methods."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.client = httpx.Client(base_url=BASE_URL, timeout=timeout)

    def get_markets(self, *, limit: int = 1000, cursor: str | None = None, status: str = "open") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "status": status}
        if cursor:
            params["cursor"] = cursor
        response = self.client.get("/markets", params=params)
        response.raise_for_status()
        return response.json()

    def get_market(self, ticker: str) -> dict[str, Any]:
        response = self.client.get(f"/markets/{ticker}")
        response.raise_for_status()
        return response.json()

def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def outcome_is_same_utc_day(market: dict[str, Any], now: datetime | None = None) -> bool:
    """Conservative first-pass filter; contract-specific timezone logic comes next."""
    now = now or datetime.now(timezone.utc)
    expiry = _parse_dt(market.get("expected_expiration_time") or market.get("expiration_time") or market.get("close_time"))
    return bool(expiry and expiry.astimezone(timezone.utc).date() == now.astimezone(timezone.utc).date())
