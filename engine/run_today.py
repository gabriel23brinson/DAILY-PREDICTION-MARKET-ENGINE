from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
from .kalshi import KalshiPublicClient
from .scanner import scan_same_day
from .eligibility import evaluate_market
from .pipeline import PipelineResult, research_market
from .resolver import resolve_pending

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
class ResearchFailure:
    ticker: str
    error: str

@dataclass(frozen=True)
class EarlyPass:
    ticker: str
    reason: str

@dataclass(frozen=True)
class DailyRun:
    scanned_same_day: int
    supported: int
    researched: int
    paper: int
    passed: int
    ranked: list[RankedCandidate]
    failures: list[ResearchFailure] = field(default_factory=list)
    early_passes: list[EarlyPass] = field(default_factory=list)

def run_today(*, client: KalshiPublicClient | None=None, persist: bool=False,
              researcher: Callable[...,PipelineResult]=research_market, **research_kwargs: Any) -> DailyRun:
    summary=discover_today(client)
    ranked=[]
    failures=[]
    early_passes=[]
    for candidate in summary.candidates:
        market=candidate["market"]
        try:
            result=researcher(market,persist=persist,**research_kwargs)
        except Exception as exc:
            failures.append(ResearchFailure(str(market.get("ticker") or ""),f"{type(exc).__name__}: {exc}"))
            continue
        if result.research is not None:
            ranked.append(RankedCandidate(market,result))
        elif result.status=="PASS":
            early_passes.append(EarlyPass(str(market.get("ticker") or ""),result.reason))
    ranked.sort(key=lambda x: x.result.research.edge.net_edge,reverse=True)
    paper=sum(1 for x in ranked if x.result.status=="PAPER")
    passed=sum(1 for x in ranked if x.result.status=="PASS") + len(early_passes)
    return DailyRun(summary.scanned_same_day,summary.supported,len(ranked),paper,passed,ranked,failures,early_passes)


@dataclass(frozen=True)
class OperationalCycle:
    daily: DailyRun
    resolutions_checked: int
    resolutions_completed: int

def run_operational_cycle(*, client: KalshiPublicClient | None=None, persist: bool=True,
                          researcher: Callable[...,PipelineResult]=research_market,
                          resolver: Callable[...,dict[str,int]]=resolve_pending,
                          **research_kwargs: Any) -> OperationalCycle:
    daily=run_today(client=client,persist=persist,researcher=researcher,**research_kwargs)
    resolution=resolver(client=client)
    return OperationalCycle(daily,resolution.get("checked",0),resolution.get("resolved",0))
