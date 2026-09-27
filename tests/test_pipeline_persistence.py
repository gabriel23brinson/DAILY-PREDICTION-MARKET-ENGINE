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


class FakeCoinbase:
    def ticker(self, product_id):
        assert product_id=="BTC-USD"
        return {"price":"100000"}
    def candles(self, product_id):
        return [[3,0,0,0,100100,0],[2,0,0,0,100000,0],[1,0,0,0,99900,0]]

def test_crypto_pipeline_reaches_research_without_weather_station():
    market={
        "ticker":"KXBTC-TEST",
        "title":"Will Bitcoin price be above $99,000 today?",
        "rules_primary":"The market resolves using the Bitcoin price reported by Coinbase.",
        "floor_strike":99000,
        "yes_ask_dollars":"0.50",
    }
    r=research_market(market,coinbase=FakeCoinbase())
    assert r.status in {"PAPER","PASS"}
    assert r.research is not None
    assert r.research.ticker=="KXBTC-TEST"
    assert r.research.probability.method=="lognormal_intraday_v0"
