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


def test_weather_semantics_without_settlement_authority_fail_closed():
    m={"ticker":"WX","title":"Highest temperature in Atlanta today?","rules_primary":"Resolves after the day ends.","floor_strike":90}
    c=parse_contract(m)
    assert c.kind == ContractKind.WEATHER_DAILY_HIGH
    assert c.settlement_source is None
    assert not evaluate_market(m).eligible

def test_weather_company_domain_identifies_settlement_authority():
    m={"ticker":"WX","title":"Lowest temperature in Miami today?","rules_primary":"Settlement is based on the final value published at weather.com.","cap_strike":72}
    c=parse_contract(m)
    assert c.kind == ContractKind.WEATHER_DAILY_LOW
    assert c.settlement_source == "The Weather Company"
    assert evaluate_market(m).eligible

def test_temperature_word_in_nonweather_contract_does_not_create_hourly_weather():
    m={"ticker":"X","title":"Will a player mention temperature at 5 PM?","rules_primary":"Determined by the National Weather Service."}
    c=parse_contract(m)
    assert c.kind == ContractKind.UNKNOWN
    assert not evaluate_market(m).eligible


def test_daily_high_weather_contract_with_station_is_supported():
    m={
        "ticker":"KXHIGH-TEST",
        "title":"Highest temperature in Atlanta today?",
        "rules_primary":"Determined by the National Weather Service final climate report for KATL.",
        "floor_strike":90,
    }
    parsed=parse_contract(m)
    assert parsed.kind == ContractKind.WEATHER_DAILY_HIGH
    assert parsed.settlement_source == "National Weather Service"
    assert parsed.floor_strike == 90
    assert evaluate_market(m).eligible

def test_daily_low_noaa_contract_is_supported():
    m={
        "ticker":"KXLOW-TEST",
        "title":"Lowest temperature in Atlanta today?",
        "rules_primary":"Resolved using NOAA/NCEI final climate observations for KATL.",
        "cap_strike":70,
    }
    parsed=parse_contract(m)
    assert parsed.kind == ContractKind.WEATHER_DAILY_LOW
    assert parsed.settlement_source == "NOAA/NCEI"
    assert parsed.cap_strike == 70
    assert evaluate_market(m).eligible


def test_supported_weather_without_numeric_strike_is_ineligible_early():
    m={"ticker":"WX","title":"Highest temperature in Atlanta today?","rules_primary":"Determined by the National Weather Service final climate report for KATL."}
    e=evaluate_market(m)
    assert not e.eligible
    assert "missing numeric strike" in e.reason

def test_supported_weather_with_inverted_interval_is_ineligible_early():
    m={"ticker":"WX","title":"Highest temperature in Atlanta today?","rules_primary":"Determined by the National Weather Service final climate report for KATL.","floor_strike":90,"cap_strike":80}
    e=evaluate_market(m)
    assert not e.eligible
    assert "invalid strike interval" in e.reason


def test_synoptic_hourly_temperature_contract_is_supported():
    m={
        "ticker":"KXTEMPCHIHS-26SEP1919-T71.99",
        "title":"Will the temp in Chicago Metro Area be above 71.99° on Sep 19, 2026 at 7pm EDT?",
        "yes_sub_title":"72° or above",
        "rules_primary":"If the temperature recorded at Chicago Metro Area for Sep 19, 2026 at 7 PM EDT as reported by Synoptic Data, is above 71.99°, then the market resolves to Yes.",
        "floor_strike":71.99,
    }
    parsed=parse_contract(m)
    assert parsed.kind == ContractKind.WEATHER_HOURLY_TEMP
    assert parsed.settlement_source == "Synoptic Data"
    assert parsed.floor_strike == 71.99
    assert parsed.parse_confidence == "high"
    assert evaluate_market(m).eligible
