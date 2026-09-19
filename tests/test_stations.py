from engine.stations import extract_station_target

def test_extract_station_and_coords():
    t=extract_station_target({"rules_primary":"Observed at KATL station coordinates 33.6407, -84.4277."})
    assert t.station_id=="KATL"
    assert t.latitude==33.6407
    assert t.longitude==-84.4277

def test_missing_station_fails():
    t=extract_station_target({"rules_primary":"Some vague weather rule."})
    assert t.confidence=="fail"
