from engine.run_today import discover_today

class FakeClient:
    def get_markets(self, **kwargs):
        return {"markets":[
          {"ticker":"W1","title":"Highest temperature today?","rules_primary":"National Weather Service","expected_expiration_time":"2099-01-01T22:00:00Z"},
        ],"cursor":None}

def test_discovery_structure(monkeypatch):
    import engine.run_today as rt
    monkeypatch.setattr(rt,"scan_same_day",lambda client:[{"ticker":"W1","title":"Highest temperature today?","rules_primary":"National Weather Service"}])
    s=discover_today(FakeClient())
    assert s.scanned_same_day==1
    assert s.supported==1
