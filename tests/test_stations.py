from engine.stations import extract_station_target

def test_extract_station_and_coords():
    t=extract_station_target({"rules_primary":"Observed at KATL station coordinates 33.6407, -84.4277."})
    assert t.station_id=="KATL"
    assert t.latitude==33.6407
    assert t.longitude==-84.4277

def test_missing_station_fails():
    t=extract_station_target({"rules_primary":"Some vague weather rule."})
    assert t.confidence=="fail"


def test_station_extraction_is_case_insensitive_and_normalized():
    t=extract_station_target({"rules_primary":"Settlement uses observations from katl."})
    assert t.station_id=="KATL"
    assert t.confidence=="high"

def test_invalid_coordinates_do_not_pass_target_validation():
    t=extract_station_target({"rules_primary":"Station coordinates 95.0, -200.0."})
    assert t.latitude is None
    assert t.longitude is None
    assert t.confidence=="fail"

def test_non_station_word_does_not_match_icao():
    t=extract_station_target({"rules_primary":"The market resolves from known final weather data."})
    assert t.station_id is None
    assert t.confidence=="fail"
