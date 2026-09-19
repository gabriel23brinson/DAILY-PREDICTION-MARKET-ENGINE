from collections import Counter
import httpx
from engine.kalshi import KalshiPublicClient, occurrence_is_same_utc_day
from engine.schema_validation import validate_market_payload
from engine.contracts import parse_contract

DETAIL_SAMPLE = 25
MAX_PAGES = 50


def discover_same_day(client):
    """Page discovery until same-day contracts are found or Kalshi is exhausted.

    The first /markets page is ranking/pagination order, not a promise that today's
    contracts appear in the first 1,000 records. Never interpret an empty first-page
    cohort as proof that no same-day markets exist.
    """
    cursor = None
    discovered = 0
    same_day = []
    pages = 0
    while pages < MAX_PAGES:
        payload = client.get_markets(limit=1000, cursor=cursor, status="open")
        markets = payload.get("markets", [])
        pages += 1
        discovered += len(markets)
        same_day.extend(m for m in markets if occurrence_is_same_utc_day(m))
        cursor = payload.get("cursor")
        if same_day or not cursor or not markets:
            break
    return discovered, pages, same_day, cursor


def main() -> None:
    client = KalshiPublicClient()
    discovered, pages, same_day, remaining_cursor = discover_same_day(client)
    if not discovered:
        raise SystemExit("FAIL: Kalshi returned zero open markets")
    print(f"open_markets_discovered={discovered}")
    print(f"discovery_pages={pages}")
    if not same_day:
        suffix = " (page safety cap reached)" if remaining_cursor else ""
        raise SystemExit(f"FAIL: no same-day occurrence markets found after discovery{suffix}")

    details = []
    hydration_failures = []
    for summary in same_day[:DETAIL_SAMPLE]:
        ticker = summary.get("ticker")
        if not ticker:
            hydration_failures.append((None, "summary missing ticker"))
            continue
        try:
            response = client.get_market(ticker)
            market = response.get("market", response)
            details.append(market)
        except httpx.HTTPStatusError as exc:
            hydration_failures.append((ticker, exc.response.status_code, exc.response.text[:160]))
        except Exception as exc:
            hydration_failures.append((ticker, type(exc).__name__, str(exc)[:160]))

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

    print(f"same_day_markets_discovered={len(same_day)}")
    print(f"detail_markets_validated={len(details)}")
    print(f"schema_valid={len(details)-len(schema_fail)} schema_failed={len(schema_fail)}")
    print("contract_kinds=", dict(kinds))
    unknown_samples = [
        {
            "ticker": m.get("ticker"),
            "event_ticker": m.get("event_ticker"),
            "title": m.get("title"),
            "subtitle": m.get("subtitle"),
            "yes_sub_title": m.get("yes_sub_title"),
            "rules_primary": (m.get("rules_primary") or "")[:500],
        }
        for m in details if parse_contract(m).kind.value == "unknown"
    ]
    if unknown_samples:
        print("unknown_contract_samples=", unknown_samples[:5])
    print("warnings=", dict(warnings))
    if schema_fail:
        print("first_schema_failures=", schema_fail[:10])
        raise SystemExit(1)
    print("PASS: live same-day Kalshi market details match the V1 structural contract")


if __name__ == "__main__":
    main()
