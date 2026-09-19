from __future__ import annotations
from dataclasses import dataclass
from .scoring import brier, log_loss

@dataclass(frozen=True)
class ResolutionScore:
    outcome: str
    brier_score: float | None
    log_loss: float | None

def score_resolution(probability_yes: float, outcome: str) -> ResolutionScore:
    if outcome=="VOID":
        return ResolutionScore(outcome,None,None)
    if outcome not in {"YES","NO"}:
        raise ValueError("outcome must be YES, NO, or VOID")
    y=1 if outcome=="YES" else 0
    return ResolutionScore(outcome,brier(probability_yes,y),log_loss(probability_yes,y))
