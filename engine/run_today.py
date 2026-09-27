from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from .kalshi import KalshiPublicClient
from .scanner import scan_same_day
from .eligibility import evaluate_market
from .pipeline import PipelineResult, research_market

@dataclass(frozen=True)
class ScanSummary:
    scanned_same_day: int
    supported: int
    rejected: int
    candidates: list[dict[str,Any]]

@dataclass(frozen=True)
class RankedCandidate:
    market: dict[str,Any]
    result: PipelineResult

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

def research_candidates(summary: ScanSummary, *, researcher: Callable[...,PipelineResult]=research_market,
                        persist: bool=False, **research_kwargs: Any) -> list[RankedCandidate]:
    ranked=[]
    for candidate in summary.candidates:
        market=candidate["market"]
        try:
            result=researcher(market,persist=persist,**research_kwargs)
        except Exception:
            continue
        if result.research is not None:
            ranked.append(RankedCandidate(market,result))
    return sorted(ranked,key=lambda x: x.result.research.edge.net_edge,reverse=True)


@dataclass(frozen=True)
class DailyRun:
    scanned_same_day: int
    supported: int
    researched: int
    paper: int
    passed: int
    ranked: list[RankedCandidate]

def run_today(*, client: KalshiPublicClient | None=None, persist: bool=False,
              researcher: Callable[...,PipelineResult]=research_market, **research_kwargs: Any) -> DailyRun:
    summary=discover_today(client)
    ranked=research_candidates(summary,researcher=researcher,persist=persist,**research_kwargs)
    paper=sum(1 for x in ranked if x.result.status=="PAPER")
    passed=sum(1 for x in ranked if x.result.status=="PASS")
    return DailyRun(summary.scanned_same_day,summary.supported,len(ranked),paper,passed,ranked)
