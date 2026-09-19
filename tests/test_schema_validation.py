from engine.schema_validation import validate_market_payload

BASE={"ticker":"T","event_ticker":"E","title":"Weather","rules_primary":"Rules",
      "occurrence_datetime":"2026-09-19T18:00:00Z","yes_ask_dollars":"0.5600"}

def test_current_schema_valid():
    c=validate_market_payload(BASE)
    assert c.valid

def test_bad_dollar_probability_fails():
    c=validate_market_payload({**BASE,"yes_ask_dollars":"56"})
    assert not c.valid

def test_missing_timing_fails_closed():
    m={k:v for k,v in BASE.items() if k!="occurrence_datetime"}
    assert not validate_market_payload(m).valid
