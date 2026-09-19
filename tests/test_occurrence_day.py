from datetime import datetime, timezone
from engine.kalshi import occurrence_date, occurrence_is_same_utc_day

NOW=datetime(2026,9,19,12,tzinfo=timezone.utc)

def test_occurrence_today_even_if_settlement_tomorrow():
    m={"occurrence_datetime":"2026-09-19T23:00:00Z","expected_expiration_time":"2026-09-20T12:00:00Z"}
    assert occurrence_is_same_utc_day(m,NOW)

def test_occurrence_tomorrow_rejected_even_if_close_today():
    m={"occurrence_datetime":"2026-09-20T01:00:00Z","close_time":"2026-09-19T23:00:00Z"}
    assert not occurrence_is_same_utc_day(m,NOW)

def test_live_summary_can_use_dated_event_ticker_when_occurrence_field_missing():
    m={"event_ticker":"KXMLBTOTAL-26SEP191605MILBAL","expected_expiration_time":"2026-09-20T04:40:00Z"}
    assert occurrence_is_same_utc_day(m,NOW)

def test_market_ticker_date_fallback():
    m={"ticker":"KXHIGHNY-26SEP19-T80"}
    assert occurrence_date(m).isoformat()=="2026-09-19"

def test_expiration_alone_does_not_define_occurrence():
    m={"expected_expiration_time":"2026-09-19T23:00:00Z","close_time":"2026-09-19T22:00:00Z"}
    assert not occurrence_is_same_utc_day(m,NOW)

def test_invalid_ticker_date_fails_closed():
    m={"event_ticker":"KXTHING-26FEB31"}
    assert occurrence_date(m) is None
