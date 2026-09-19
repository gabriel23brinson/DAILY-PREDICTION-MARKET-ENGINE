from engine.pipeline import PipelineResult, research_market

def test_pipeline_result_tracks_prediction_id():
    r=PipelineResult("PAPER","test",prediction_id=123)
    assert r.prediction_id==123


def test_pipeline_fails_closed_when_contract_has_station_but_no_coordinates():
    market={
        "ticker":"KXHIGH-TEST",
        "title":"Highest temperature in Atlanta today?",
        "rules_primary":"Determined by the National Weather Service final climate report for KATL.",
        "floor_strike":90,
        "yes_ask_dollars":"0.50",
    }
    r=research_market(market,nws_user_agent="test@example.com")
    assert r.status=="PASS"
    assert "coordinates" in r.reason
    assert r.research is None
