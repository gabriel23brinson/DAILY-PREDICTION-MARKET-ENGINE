from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from typing import Any
from pydantic import BaseModel, Field

class SourceTier(str, Enum):
    SETTLEMENT = "settlement"
    PRIMARY = "primary"
    INDEPENDENT = "independent"
    MARKET = "market"
    HISTORICAL = "historical"

class EvidenceItem(BaseModel):
    provider: str
    source_tier: SourceTier
    endpoint: str
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    observed_at: datetime | None = None
    value: Any
    units: str | None = None
    stale: bool = False
    critical: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def payload_hash(self) -> str:
        body = json.dumps(self.value, sort_keys=True, default=str, separators=(",", ":"))
        return sha256(body.encode()).hexdigest()

class EvidenceBundle(BaseModel):
    market_ticker: str
    items: list[EvidenceItem] = Field(default_factory=list)

    def critical_failure(self) -> str | None:
        critical = [x for x in self.items if x.critical]
        if not critical:
            return "missing critical evidence"
        stale = [x.provider for x in critical if x.stale]
        if stale:
            return f"stale critical evidence: {', '.join(stale)}"
        return None
