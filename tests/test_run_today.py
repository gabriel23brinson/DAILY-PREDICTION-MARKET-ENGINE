from engine.run_today import discover_today

class FakeClient:
    def get_markets(self, **kwargs):
        return {"markets":[
          {"ticker":"W1","title":"Highest temperature today?","rules_primary":"National Weather Service","expected_expiration_time":"2099-01-01T22:00:00Z"},
        ],"cursor":None}

def test_discovery_structure(monkeypatch):
    import engine.run_today as rt
    monkeypatch.setattr(rt,"scan_same_day",lambda client:[{"ticker":"W1","title":"Highest temperature today?","rules_primary":"National Weather Service","floor_strike":80}])
    s=discover_today(FakeClient())
    assert s.scanned_same_day==1
    assert s.supported==1


def test_research_candidates_ranks_highest_net_edge_first():
    from decimal import Decimal
    from engine.run_today import ScanSummary, research_candidates
    from engine.pipeline import PipelineResult
    from engine.research import ResearchResult
    from engine.probability import ProbabilityEstimate
    from engine.edge import EdgeResult

    markets=[{"ticker":"LOW"},{"ticker":"HIGH"}]
    summary=ScanSummary(2,2,0,[{"market":m,"contract":None} for m in markets])
    def fake_research(market, **kwargs):
        edge=Decimal(".10") if market["ticker"]=="HIGH" else Decimal(".02")
        rr=ResearchResult(market["ticker"],ProbabilityEstimate(.6,1,1,"test"),
            EdgeResult("YES",Decimal(".6"),Decimal(".5"),edge,Decimal("0"),edge,"PAPER","test"),{})
        return PipelineResult("PAPER","test",rr)
    ranked=research_candidates(summary,researcher=fake_research)
    assert [x.market["ticker"] for x in ranked]==["HIGH","LOW"]
