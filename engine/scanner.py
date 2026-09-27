from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from .kalshi import KalshiPublicClient, outcome_is_same_utc_day

WEATHER_SERIES_HINTS=("temperature","daily high","daily low")

def _direct_same_day_weather(client: KalshiPublicClient, now: datetime) -> list[dict[str,Any]]:
    payload=client.get_series_list()
    series=payload.get("series",[])
    candidates=[
        x for x in series
        if any(h in str(x.get("title") or "").lower() for h in WEATHER_SERIES_HINTS)
        or str(x.get("ticker") or "").upper().startswith(("KXHIGH","KXLOW"))
    ]
    for item in candidates:
        ticker=item.get("ticker")
        if not ticker: continue
        markets=client.get_markets(limit=1000,status="open",series_ticker=ticker).get("markets",[])
        same=[m for m in markets if outcome_is_same_utc_day(m,now)]
        if same: return same
    return []

def scan_same_day(client: KalshiPublicClient | None = None, max_pages: int = 20) -> list[dict[str, Any]]:
    client = client or KalshiPublicClient()
    out: list[dict[str, Any]] = []
    cursor: str | None = None
    now = datetime.now(timezone.utc)
    direct=_direct_same_day_weather(client,now)
    if direct:
        out.extend(direct)
    for _ in range(max_pages):
        payload = client.get_markets(cursor=cursor)
        markets = payload.get("markets", [])
        out.extend(m for m in markets if outcome_is_same_utc_day(m, now))
        cursor = payload.get("cursor")
        if not cursor or not markets:
            break
    dedup={m.get("ticker"):m for m in out if m.get("ticker")}
    return list(dedup.values())
