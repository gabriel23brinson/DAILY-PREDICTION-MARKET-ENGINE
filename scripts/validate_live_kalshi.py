from collections import Counter
from engine.kalshi import KalshiPublicClient
from engine.schema_validation import validate_market_payload
from engine.contracts import parse_contract

DETAIL_SAMPLE = 25


def main() -> None:
    client = KalshiPublicClient()
    payload = client.get_markets(limit=1000, status="open")
    summaries = payload.get("markets", [])
    if not summaries:
        raise SystemExit("FAIL: Kalshi returned zero open markets")

    # The collection endpoint is discovery data and may omit rules_primary.
    # Hydrate individual markets before validating the full contract schema.
    details = []
    hydration_failures = []
    for summary in summaries[:DETAIL_SAMPLE]:
        ticker = summary.get("ticker")
        if not ticker:
            hydration_failures.append((None, "summary missing ticker"))
            continue
        try:
            response = client.get_market(ticker)
            market = response.get("market", response)
            details.append(market)
        except Exception as exc:
            hydration_failures.append((ticker, type(exc).__name__))

    if hydration_failures:
        print("hydration_failures=", hydration_failures[:10])
        raise SystemExit(1)
    if not details:
        raise SystemExit("FAIL: no market detail payloads hydrated")

    schema_fail = []
    warnings = Counter()
    kinds = Counter()
    for market in details:
        check = validate_market_payload(market)
        if not check.valid:
            schema_fail.append((market.get("ticker"), check.errors))
        warnings.update(check.warnings)
        kinds[parse_contract(market).kind.value] += 1

    print(f"open_markets_discovered={len(summaries)}")
    print(f"detail_markets_validated={len(details)}")
    print(f"schema_valid={len(details)-len(schema_fail)} schema_failed={len(schema_fail)}")
    print("contract_kinds=", dict(kinds))
    print("warnings=", dict(warnings))
    if schema_fail:
        print("first_schema_failures=", schema_fail[:10])
        raise SystemExit(1)
    print("PASS: hydrated live Kalshi market details match the V1 structural contract")


if __name__ == "__main__":
    main()
