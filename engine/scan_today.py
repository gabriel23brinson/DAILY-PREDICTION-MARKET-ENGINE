from __future__ import annotations
from dataclasses import dataclass
import os
from .kalshi import KalshiPublicClient
from .run_today import discover_today
from .pipeline import research_market
from .resolver import resolve_pending

@dataclass(frozen=True)
class DailyRun:
    same_day: int
    supported: int
    paper: int
    passed: int
    failed: int
    newly_resolved: int
    results: list

def run_today(*, persist: bool=True) -> DailyRun:
    client=KalshiPublicClient()
    discovery=discover_today(client)
    results=[]
    paper=passed=failed=0
    ua=os.environ.get("NWS_USER_AGENT","")
    if not ua:
        raise RuntimeError("NWS_USER_AGENT is required")
    for candidate in discovery.candidates:
        market=candidate["market"]
        try:
            r=research_market(market,nws_user_agent=ua,persist=persist)
            results.append(r)
            if r.status=="PAPER": paper+=1
            else: passed+=1
        except Exception as exc:
            failed+=1
            results.append({"ticker":market.get("ticker"),"status":"ERROR","reason":str(exc)})
    resolved=0
    if persist:
        resolved=resolve_pending(client=client)["resolved"]
    return DailyRun(discovery.scanned_same_day,discovery.supported,paper,passed,failed,resolved,results)
