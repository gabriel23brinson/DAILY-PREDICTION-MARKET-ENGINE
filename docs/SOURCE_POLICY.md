# Source and Settlement Policy

1. Contract terms are parsed before modeling.
2. The settlement source named in the contract controls resolution.
3. Primary sources are preferred for factual inputs.
4. Multiple representations of one upstream source are correlated evidence, not independent votes.
5. Preliminary and final/QC observations are stored distinctly.
6. Every prediction stores timestamped evidence provenance.
7. Missing or ambiguous rules, source identity, time window, location/station, or strike semantics => PASS.
8. A model probability is never substituted for settlement truth.
9. Executable bid/ask is distinct from midpoint/last trade.
10. V0.1 is paper-only.

Weather specifics:
- Daily temperature contracts: use the exact NWS climate report/station named by Kalshi rules.
- Hourly temperature contracts: use The Weather Company value/station coordinates named by Kalshi rules.
- Day boundary/time-zone semantics must follow the contract and source, not generic calendar assumptions.
