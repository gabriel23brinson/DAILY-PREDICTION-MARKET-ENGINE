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
    return Eligibility(True, "supported contract with identified settlement source", c)
