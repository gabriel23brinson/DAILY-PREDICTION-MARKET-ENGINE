from engine.pipeline import PipelineResult

def test_pipeline_result_tracks_prediction_id():
    r=PipelineResult("PAPER","test",prediction_id=123)
    assert r.prediction_id==123
