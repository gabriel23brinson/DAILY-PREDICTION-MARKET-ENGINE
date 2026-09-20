from datetime import datetime, timezone
from decimal import Decimal
from engine.weather_model import build_temperature_input
from engine.research import WeatherResearchAdapter, research_weather_contract, research_with_adapter

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


def test_stale_critical_weather_evidence_blocks_research():
    w=build_temperature_input(ticker="X",nws_payload=payload(),retrieved_at=datetime.now(timezone.utc))
    stale=w.evidence.model_copy(deep=True)
    stale.items[0].stale=True
    from engine.weather_model import WeatherModelInput
    blocked=WeatherModelInput(w.mean_f,w.sigma_f,stale,w.diagnostics)
    try:
        research_weather_contract(ticker="X",weather=blocked,floor=65,cap=80,yes_ask=Decimal(".50"))
    except ValueError as exc:
        assert "stale critical evidence" in str(exc)
        return
    assert False


def test_weather_adapter_uses_generic_research_boundary():
    w=build_temperature_input(ticker="X",nws_payload=payload(),retrieved_at=datetime.now(timezone.utc))
    adapter=WeatherResearchAdapter(weather=w,floor=65,cap=80)
    r=research_with_adapter(adapter=adapter,ticker="X",yes_ask=Decimal(".50"))
    assert r.ticker=="X"
    assert r.edge.decision in {"PAPER","PASS"}

def test_generic_research_boundary_rejects_mismatched_ticker():
    w=build_temperature_input(ticker="X",nws_payload=payload(),retrieved_at=datetime.now(timezone.utc))
    adapter=WeatherResearchAdapter(weather=w,floor=65,cap=80)
    try:
        research_with_adapter(adapter=adapter,ticker="OTHER",yes_ask=Decimal(".50"))
    except ValueError as exc:
        assert "mismatched ticker" in str(exc)
        return
    assert False
