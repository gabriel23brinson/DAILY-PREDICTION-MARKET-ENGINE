from decimal import Decimal
from engine.probability import interval_probability
from engine.edge import evaluate_edge
from engine.scoring import brier, log_loss

def test_interval_probability_is_bounded():
    p=interval_probability(80,3,78,82)
    assert 0 < p < 1

def test_missing_executable_price_passes():
    r=evaluate_edge(side="YES",model_probability=Decimal(".70"),executable_price=None)
    assert r.decision=="PASS"

def test_edge_threshold():
    r=evaluate_edge(side="YES",model_probability=Decimal(".70"),executable_price=Decimal(".60"),estimated_cost=Decimal(".01"),minimum_net_edge=Decimal(".05"))
    assert r.decision=="PAPER"
    assert r.net_edge==Decimal(".09")

def test_scoring_prefers_accurate_probability():
    assert brier(.9,1) < brier(.6,1)
    assert log_loss(.9,1) < log_loss(.6,1)
