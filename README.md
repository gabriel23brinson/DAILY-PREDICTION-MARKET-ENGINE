# DAILY PREDICTION MARKET ENGINE

A research-first Python system for short-duration prediction markets.

## V0.1 contract
- Same-day underlying outcomes only.
- Paper predictions only; no order execution.
- Settlement rules/source are first-class evidence.
- Primary/official sources outrank aggregators.
- Every prediction stores an immutable evidence snapshot.
- Fail closed on stale, missing, contradictory, or ambiguous critical evidence.
- Measure probability quality with Brier score, log loss, and calibration.
- Add model families only when they have defensible data and settlement mapping.

## Pipeline
Kalshi market discovery -> same-day eligibility -> settlement verification -> source adapters -> category model -> executable-price comparison -> PAPER/PASS -> Supabase ledger -> resolution -> calibration.

## Source philosophy
Source count is not a vote. Correlated copies do not become independent evidence. Each source receives provenance metadata (provider, endpoint, retrieval time, observed/published time where available, freshness, role, and raw payload hash). Settlement authority and primary data have highest priority.

## Initial family
Weather is the first model family because NWS provides official forecasts/observations and NOAA/NCEI provides historical climate data. The architecture is category-agnostic so crypto, financial, commodity, and other same-day families can be added behind the same evidence contract.

## Safety
Research software. No guarantee of profit. V0.1 does not place trades.


## Milestone 2 — live weather contract interpretation
Goal: promote a live same-day Kalshi weather market from discovery into a defensible research candidate without weakening fail-closed behavior.

Completion criteria:
1. Identify and hydrate a live same-day weather contract when Kalshi has one available.
2. Parse its temperature contract kind and numeric strike semantics from the hydrated payload.
3. Identify the contract's settlement authority/source from its rules.
4. Extract a defensible station or geographic target required by the weather evidence adapter.
5. Reject unrelated, ambiguous, or unsupported contracts before modeling.
6. Preserve a real live payload shape as a regression fixture/test.
7. Pass the full unit suite and live validation; lack of an available same-day specimen is reported as NO_DATA rather than a code failure.
