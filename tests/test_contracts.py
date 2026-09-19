from engine.contracts import ContractKind, parse_contract
from engine.eligibility import evaluate_market

def test_daily_high_nws():
    m={"ticker":"X","title":"Highest temperature in Chicago today?","rules_primary":"Determined by the National Weather Service final climate report.","floor_strike":80}
    c=parse_contract(m)
    assert c.kind == ContractKind.WEATHER_DAILY_HIGH
    assert c.settlement_source == "National Weather Service"
    assert evaluate_market(m).eligible

def test_hourly_weather_company():
    m={"ticker":"X","title":"Chicago temperature at 5 PM?","rules_primary":"Determined by The Weather Company."}
    c=parse_contract(m)
    assert c.kind == ContractKind.WEATHER_HOURLY_TEMP
    assert c.settlement_source == "The Weather Company"

def test_missing_rules_fails_closed():
    m={"ticker":"X","title":"Highest temperature in Chicago today?"}
    assert not evaluate_market(m).eligible

def test_unknown_contract_fails_closed():
    m={"ticker":"X","title":"Something unrelated","rules_primary":"Some source"}
    assert not evaluate_market(m).eligible


def test_unrelated_live_soccer_total_stays_unsupported():
    m={
        "ticker":"KXARGNACBTOTAL-26SEP19CATALM-7",
        "event_ticker":"KXARGNACBTOTAL-26SEP19CATALM",
        "title":"Will over 6.5 goals be scored?",
        "yes_sub_title":"Over 6.5 goals scored",
        "rules_primary":"If over 6.5 goals are scored in the Temperley vs Almagro professional Argentine Nacional B soccer game originally scheduled for Sep 19, 2026 after 90 minutes plus stoppage time (does not include extra time or penalties), then the market resolves to Yes.",
    }
    c=parse_contract(m)
    assert c.kind == ContractKind.UNKNOWN
    assert not evaluate_market(m).eligible
