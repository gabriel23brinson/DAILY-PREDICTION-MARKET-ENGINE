from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .contracts import ContractKind, ParsedContract, parse_contract

@dataclass(frozen=True)
class Eligibility:
    eligible: bool
    reason: str
    contract: ParsedContract

SUPPORTED={
    ContractKind.WEATHER_DAILY_HIGH,
    ContractKind.WEATHER_DAILY_LOW,
    ContractKind.WEATHER_HOURLY_TEMP,
}

def evaluate_market(m: dict[str, Any]) -> Eligibility:
    c=parse_contract(m)
    if c.kind not in SUPPORTED:
        return Eligibility(False, c.fail_reason or "unsupported model family", c)
    if c.fail_reason:
        return Eligibility(False, c.fail_reason, c)
    if c.floor_strike is None and c.cap_strike is None:
        return Eligibility(False, "supported weather contract missing numeric strike bounds", c)
    if c.floor_strike is not None and c.cap_strike is not None and c.floor_strike >= c.cap_strike:
        return Eligibility(False, "supported weather contract has invalid strike interval", c)
    return Eligibility(True, "supported contract with identified settlement source and strike bounds", c)
