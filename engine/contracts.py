from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import re
from typing import Any

class ContractKind(str, Enum):
    WEATHER_DAILY_HIGH = "weather_daily_high"
    WEATHER_DAILY_LOW = "weather_daily_low"
    WEATHER_HOURLY_TEMP = "weather_hourly_temp"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class ParsedContract:
    ticker: str
    kind: ContractKind
    rules_primary: str
    settlement_source: str | None
    floor_strike: float | None
    cap_strike: float | None
    functional_strike: str | None
    parse_confidence: str
    fail_reason: str | None = None

def _source(rules: str) -> str | None:
    low=rules.lower()
    if "weather company" in low or "weather.com" in low:
        return "The Weather Company"
    if "national weather service" in low or re.search(r"\bnws\b", low):
        return "National Weather Service"
    if "noaa" in low or "ncei" in low:
        return "NOAA/NCEI"
    return None

def parse_contract(m: dict[str, Any]) -> ParsedContract:
    rules=(m.get("rules_primary") or "").strip()
    title=" ".join(str(m.get(k) or "") for k in ("title","subtitle","yes_sub_title")).lower()
    src=_source(rules)
    kind=ContractKind.UNKNOWN
    if any(x in title for x in ("highest temperature","high temperature","daily high")):
        kind=ContractKind.WEATHER_DAILY_HIGH
    elif any(x in title for x in ("lowest temperature","low temperature","daily low")):
        kind=ContractKind.WEATHER_DAILY_LOW
    elif (
        "temperature" in title
        and re.search(r"\b\d{1,2}(?::\d{2})?\s*(am|pm)\b", title)
        and not re.search(r"\b(mention|say|said|tweet|post|player|candidate|person)\b", title)
        and (
            "weather company" in rules.lower()
            or "weather.com" in rules.lower()
            or bool(re.search(r"\bK[A-Z]{3}\b", rules))
            or "station" in rules.lower()
            or "coordinates" in rules.lower()
        )
    ):
        kind=ContractKind.WEATHER_HOURLY_TEMP
    reasons=[]
    if not rules: reasons.append("missing rules_primary")
    if kind is ContractKind.UNKNOWN: reasons.append("unsupported/unknown contract semantics")
    if kind is not ContractKind.UNKNOWN and not src: reasons.append("settlement source not identified from rules")
    return ParsedContract(
        ticker=str(m.get("ticker") or ""),
        kind=kind,
        rules_primary=rules,
        settlement_source=src,
        floor_strike=m.get("floor_strike"),
        cap_strike=m.get("cap_strike"),
        functional_strike=m.get("functional_strike"),
        parse_confidence="high" if not reasons else "fail",
        fail_reason="; ".join(reasons) or None,
    )
