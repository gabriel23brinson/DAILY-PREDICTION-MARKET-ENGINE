from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class EdgeResult:
    side: str
    model_probability: Decimal
    entry_price: Decimal
    gross_edge: Decimal
    estimated_cost: Decimal
    net_edge: Decimal
    decision: str
    reason: str

def evaluate_edge(*, side: str, model_probability: Decimal, executable_price: Decimal | None,
                  estimated_cost: Decimal = Decimal("0"), minimum_net_edge: Decimal = Decimal("0.05")) -> EdgeResult:
    if executable_price is None:
        return EdgeResult(side,model_probability,Decimal("0"),Decimal("0"),estimated_cost,Decimal("0"),"PASS","no executable ask")
    if not Decimal("0") <= model_probability <= Decimal("1"):
        raise ValueError("model probability outside [0,1]")
    if not Decimal("0") < executable_price < Decimal("1"):
        return EdgeResult(side,model_probability,executable_price,Decimal("0"),estimated_cost,Decimal("0"),"PASS","invalid executable price")
    gross=model_probability-executable_price
    net=gross-estimated_cost
    decision="PAPER" if net >= minimum_net_edge else "PASS"
    reason="net edge clears threshold" if decision=="PAPER" else "insufficient net edge"
    return EdgeResult(side,model_probability,executable_price,gross,estimated_cost,net,decision,reason)
