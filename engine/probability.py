from __future__ import annotations
from dataclasses import dataclass
from math import erf, sqrt

def normal_cdf(x: float, mean: float, sigma: float) -> float:
    if sigma <= 0: raise ValueError("sigma must be positive")
    return 0.5 * (1.0 + erf((x-mean)/(sigma*sqrt(2.0))))

def interval_probability(mean: float, sigma: float, floor: float | None, cap: float | None) -> float:
    if floor is None and cap is None:
        raise ValueError("weather contract missing numeric strike bounds")
    if floor is not None and cap is not None and floor >= cap:
        raise ValueError("weather contract has invalid strike interval")
    lo=0.0 if floor is None else normal_cdf(floor, mean, sigma)
    hi=1.0 if cap is None else normal_cdf(cap, mean, sigma)
    return max(0.0, min(1.0, hi-lo))

@dataclass(frozen=True)
class ProbabilityEstimate:
    probability: float
    mean: float
    sigma: float
    method: str

def weather_interval_estimate(mean: float, sigma: float, floor: float | None, cap: float | None) -> ProbabilityEstimate:
    return ProbabilityEstimate(interval_probability(mean,sigma,floor,cap),mean,sigma,"normal_interval_v0")
