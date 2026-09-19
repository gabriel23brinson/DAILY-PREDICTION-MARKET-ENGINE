from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

@dataclass(frozen=True)
class MarketSchemaCheck:
    valid: bool
    errors: tuple[str,...]
    warnings: tuple[str,...]

def validate_market_payload(m: dict[str,Any]) -> MarketSchemaCheck:
    errors=[]; warnings=[]
    for key in ("ticker","event_ticker","title","rules_primary"):
        if not m.get(key): errors.append(f"missing {key}")
    if not any(m.get(k) for k in ("occurrence_datetime","expected_expiration_time","expiration_time","close_time")):
        errors.append("missing event/expiration timing")
    if m.get("functional_strike") and m.get("floor_strike") is None and m.get("cap_strike") is None:
        warnings.append("functional strike present without numeric floor/cap")
    for key in ("yes_bid_dollars","yes_ask_dollars","no_bid_dollars","no_ask_dollars"):
        value=m.get(key)
        if value is None: continue
        try:
            p=Decimal(str(value))
            if p < 0 or p > 1: errors.append(f"{key} outside [0,1]")
        except InvalidOperation:
            errors.append(f"{key} is not decimal")
    if not any(m.get(k) is not None for k in ("yes_ask_dollars","yes_ask")):
        warnings.append("no executable YES ask")
    return MarketSchemaCheck(not errors,tuple(errors),tuple(warnings))
