from __future__ import annotations
import json
import os
from engine.run_today import run_operational_cycle

def main() -> None:
    cycle=run_operational_cycle(
        persist=True,
        nws_user_agent=os.getenv("NWS_USER_AGENT","prediction-market-research/0.1"),
    )
    payload={
        "scanned_same_day":cycle.daily.scanned_same_day,
        "supported":cycle.daily.supported,
        "researched":cycle.daily.researched,
        "paper":cycle.daily.paper,
        "passed":cycle.daily.passed,
        "resolutions_checked":cycle.resolutions_checked,
        "resolutions_completed":cycle.resolutions_completed,
        "ranked":[
            {
                "ticker":x.market.get("ticker"),
                "decision":x.result.status,
                "probability":x.result.research.probability.probability,
                "net_edge":str(x.result.research.edge.net_edge),
            }
            for x in cycle.daily.ranked
        ],
    }
    print(json.dumps(payload,indent=2))

if __name__=="__main__":
    main()
