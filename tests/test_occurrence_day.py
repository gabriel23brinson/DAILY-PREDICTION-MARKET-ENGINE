from datetime import datetime, timezone
from engine.kalshi import occurrence_is_same_utc_day

NOW=datetime(2026,9,19,12,tzinfo=timezone.utc)

def test_occurrence_today_even_if_settlement_tomorrow():
    m={"occurrence_datetime":"2026-09-19T23:00:00Z","expected_expiration_time":"2026-09-20T12:00:00Z"}
    assert occurrence_is_same_utc_day(m,NOW)

def test_occurrence_tomorrow_rejected_even_if_close_today():
    m={"occurrence_datetime":"2026-09-20T01:00:00Z","close_time":"2026-09-19T23:00:00Z"}
    assert not occurrence_is_same_utc_day(m,NOW)

def test_missing_occurrence_fails_closed():
    m={"expected_expiration_time":"2026-09-19T23:00:00Z"}
    assert not occurrence_is_same_utc_day(m,NOW)
