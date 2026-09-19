from datetime import datetime, timezone
from engine.kalshi import outcome_is_same_utc_day

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc)

def test_same_day_expiry_is_included():
    assert outcome_is_same_utc_day({"expected_expiration_time":"2026-09-19T22:00:00Z"}, NOW)

def test_future_day_is_excluded():
    assert not outcome_is_same_utc_day({"expected_expiration_time":"2026-09-20T01:00:00Z"}, NOW)

def test_missing_expiry_fails_closed():
    assert not outcome_is_same_utc_day({}, NOW)
