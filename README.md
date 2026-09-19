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
