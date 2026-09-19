from __future__ import annotations
from math import log

EPS=1e-15

def brier(probability: float, outcome: int) -> float:
    return (probability-float(outcome))**2

def log_loss(probability: float, outcome: int) -> float:
    p=max(EPS,min(1-EPS,probability))
    return -(outcome*log(p)+(1-outcome)*log(1-p))
