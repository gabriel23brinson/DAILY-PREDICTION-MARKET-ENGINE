from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .kalshi import KalshiPublicClient
from .scanner import scan_same_day
from .eligibility import evaluate_market

@dataclass(frozen=True)
class ScanSummary:
    scanned_same_day: int
    supported: int
    rejected: int
    candidates: list[dict[str,Any]]

def discover_today(client: KalshiPublicClient | None=None) -> ScanSummary:
    client=client or KalshiPublicClient()
    markets=scan_same_day(client)
    candidates=[]
    rejected=0
    for m in markets:
        eligibility=evaluate_market(m)
        if eligibility.eligible:
            candidates.append({"market":m,"contract":eligibility.contract})
        else:
            rejected+=1
    return ScanSummary(len(markets),len(candidates),rejected,candidates)
