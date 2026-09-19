from engine.resolver import normalize_result

def test_result_normalization():
    assert normalize_result({"result":"yes"})=="YES"
    assert normalize_result({"result":"no"})=="NO"
    assert normalize_result({"result":"void"})=="VOID"
    assert normalize_result({"result":""}) is None
