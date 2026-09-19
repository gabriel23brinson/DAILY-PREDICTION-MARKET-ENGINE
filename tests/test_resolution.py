from engine.resolution import score_resolution

def test_yes_resolution_scores():
    r=score_resolution(.8,"YES")
    assert r.brier_score < .1
    assert r.log_loss > 0

def test_void_not_scored():
    r=score_resolution(.8,"VOID")
    assert r.brier_score is None and r.log_loss is None
