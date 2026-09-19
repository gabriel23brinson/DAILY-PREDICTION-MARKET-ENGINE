from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from .kalshi import KalshiPublicClient, outcome_is_same_utc_day

def scan_same_day(client: KalshiPublicClient | None = None, max_pages: int = 20) -> list[dict[str, Any]]:
    client = client or KalshiPublicClient()
    out: list[dict[str, Any]] = []
    cursor: str | None = None
    now = datetime.now(timezone.utc)
    for _ in range(max_pages):
        payload = client.get_markets(cursor=cursor)
        markets = payload.get("markets", [])
        out.extend(m for m in markets if outcome_is_same_utc_day(m, now))
        cursor = payload.get("cursor")
        if not cursor or not markets:
            break
    return out
