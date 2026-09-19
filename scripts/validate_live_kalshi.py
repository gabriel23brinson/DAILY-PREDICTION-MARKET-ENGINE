from collections import Counter
from engine.kalshi import KalshiPublicClient
from engine.schema_validation import validate_market_payload
from engine.contracts import parse_contract

def main() -> None:
    client=KalshiPublicClient()
    payload=client.get_markets(limit=1000,status="open")
    markets=payload.get("markets",[])
    if not markets:
        raise SystemExit("FAIL: Kalshi returned zero open markets")
    schema_fail=[]
    warnings=Counter()
    kinds=Counter()
    for m in markets:
        check=validate_market_payload(m)
        if not check.valid:
            schema_fail.append((m.get("ticker"),check.errors))
        warnings.update(check.warnings)
        kinds[parse_contract(m).kind.value]+=1
    print(f"open_markets_sampled={len(markets)}")
    print(f"schema_valid={len(markets)-len(schema_fail)} schema_failed={len(schema_fail)}")
    print("contract_kinds=",dict(kinds))
    print("warnings=",dict(warnings))
    if schema_fail:
        print("first_schema_failures=",schema_fail[:10])
        raise SystemExit(1)
    print("PASS: live Kalshi payloads match the V1 structural contract")

if __name__=="__main__":
    main()
