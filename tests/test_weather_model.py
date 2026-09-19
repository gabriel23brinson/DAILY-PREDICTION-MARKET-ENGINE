from datetime import datetime, timezone
from decimal import Decimal
from engine.weather_model import build_temperature_input
from engine.research import research_weather_contract

def payload():
    return {
      "grid":{"properties":{"temperature":{"values":[{"value":20.0},{"value":22.0},{"value":24.0}]}}},
      "hourly":{"properties":{"periods":[{"temperature":68},{"temperature":72},{"temperature":75}]}}
    }

def test_weather_input_has_evidence_and_uncertainty():
    w=build_temperature_input(ticker="X",nws_payload=payload(),retrieved_at=datetime.now(timezone.utc))
    assert w.sigma_f >= 2
    assert len(w.evidence.items)==2

def test_end_to_end_research_returns_decision():
    w=build_temperature_input(ticker="X",nws_payload=payload(),retrieved_at=datetime.now(timezone.utc))
    r=research_weather_contract(ticker="X",weather=w,floor=65,cap=80,yes_ask=Decimal(".50"))
    assert r.edge.decision in {"PAPER","PASS"}

def test_missing_weather_fails_closed():
    try:
        build_temperature_input(ticker="X",nws_payload={"grid":{},"hourly":{}},retrieved_at=datetime.now(timezone.utc))
    except ValueError:
        return
    assert False


def test_missing_hourly_critical_evidence_fails_closed():
    p=payload()
    p["hourly"]={}
    try:
        build_temperature_input(ticker="X",nws_payload=p,retrieved_at=datetime.now(timezone.utc))
    except ValueError as exc:
        assert "hourly" in str(exc)
        return
    assert False

def test_missing_grid_critical_evidence_fails_closed():
    p=payload()
    p["grid"]={}
    try:
        build_temperature_input(ticker="X",nws_payload=p,retrieved_at=datetime.now(timezone.utc))
    except ValueError as exc:
        assert "grid" in str(exc)
        return
    assert False
