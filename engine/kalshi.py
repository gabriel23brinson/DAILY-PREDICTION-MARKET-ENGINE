from __future__ import annotations
from datetime import date, datetime, timezone
import re
from typing import Any
import httpx
from .http_retry import with_http_retry

BASE_URL = "https://external-api.kalshi.com/trade-api/v2"
_TICKER_DATE = re.compile(r"(?:^|-)(\d{2})(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(\d{2})(?:$|[A-Z0-9-])")
_MONTHS = {m: i for i, m in enumerate(("JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"), 1)}

class KalshiPublicClient:
    """Read-only live Kalshi market-data client. No order placement methods."""
    def __init__(self, timeout: float = 15.0) -> None:
        self.client=httpx.Client(base_url=BASE_URL,timeout=timeout)
    def get_markets(self, *, limit:int=1000,cursor:str|None=None,status:str="open",series_ticker:str|None=None)->dict[str,Any]:
        params:dict[str,Any]={"limit":limit,"status":status}
        if cursor: params["cursor"]=cursor
        if series_ticker: params["series_ticker"]=series_ticker
        r=with_http_retry(lambda: _checked_get(self.client,"/markets",params=params)); return r.json()
    def get_market(self,ticker:str)->dict[str,Any]:
        r=with_http_retry(lambda: _checked_get(self.client,f"/markets/{ticker}")); return r.json()
    def get_event(self,event_ticker:str)->dict[str,Any]:
        r=with_http_retry(lambda: _checked_get(self.client,f"/events/{event_ticker}")); return r.json()
    def get_series(self,series_ticker:str)->dict[str,Any]:
        r=with_http_retry(lambda: _checked_get(self.client,f"/series/{series_ticker}")); return r.json()
    def get_series_list(self, *, category:str|None=None, tags:str|None=None)->dict[str,Any]:
        params:dict[str,Any]={}
        if category: params["category"]=category
        if tags: params["tags"]=tags
        r=with_http_retry(lambda: _checked_get(self.client,"/series",params=params or None)); return r.json()
    def get_orderbook(self,ticker:str,depth:int|None=None)->dict[str,Any]:
        params={"depth":depth} if depth is not None else None
        r=with_http_retry(lambda: _checked_get(self.client,f"/markets/{ticker}/orderbook",params=params)); return r.json()

def _parse_dt(value:str|None)->datetime|None:
    if not value: return None
    return datetime.fromisoformat(value.replace("Z","+00:00"))

def _ticker_occurrence_date(value:str|None)->date|None:
    """Extract Kalshi's YYMONDD event date when the payload omits occurrence_datetime."""
    if not value: return None
    match=_TICKER_DATE.search(value.upper())
    if not match: return None
    yy, mon, dd=match.groups()
    try:
        return date(2000+int(yy), _MONTHS[mon], int(dd))
    except ValueError:
        return None

def occurrence_date(market:dict[str,Any])->date|None:
    """Underlying event date, fail-closed.

    Prefer Kalshi's explicit occurrence_datetime when supplied. Current live market
    summaries often omit that field, while dated event/market tickers encode the
    underlying event day (for example ...-26SEP19...). We deliberately do not use
    close/expiration/settlement timestamps as a substitute.
    """
    occurrence=_parse_dt(market.get("occurrence_datetime"))
    if occurrence:
        return occurrence.astimezone(timezone.utc).date()
    return _ticker_occurrence_date(market.get("event_ticker")) or _ticker_occurrence_date(market.get("ticker"))

def occurrence_is_same_utc_day(market:dict[str,Any],now:datetime|None=None)->bool:
    now=now or datetime.now(timezone.utc)
    return occurrence_date(market)==now.astimezone(timezone.utc).date()

outcome_is_same_utc_day=occurrence_is_same_utc_day
