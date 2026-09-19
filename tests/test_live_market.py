from decimal import Decimal
from engine.live_market import _price

def test_current_dollar_price():
    assert _price({"yes_ask_dollars":"0.5600","yes_ask":56},"yes_ask_dollars","yes_ask")==Decimal("0.5600")

def test_legacy_cent_price():
    assert _price({"yes_ask":56},"yes_ask_dollars","yes_ask")==Decimal("0.56")

def test_zero_is_not_lost():
    assert _price({"yes_ask_dollars":"0.0000"},"yes_ask_dollars","yes_ask")==Decimal("0.0000")
