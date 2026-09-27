from __future__ import annotations
import argparse
import json
import os
from engine.run_today import run_today, run_operational_cycle

def _daily_payload(daily) -> dict:
    return {
        "scanned_same_day":daily.scanned_same_day,
        "supported":daily.supported,
        "researched":daily.researched,
        "paper":daily.paper,
        "passed":daily.passed,
        "ranked":[
            {
                "ticker":x.market.get("ticker"),
                "decision":x.result.status,
                "probability":x.result.research.probability.probability,
                "net_edge":str(x.result.research.edge.net_edge),
            }
            for x in daily.ranked
        ],
    }

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--smoke",action="store_true",help="research live markets without persistence or resolution")
    args=parser.parse_args()
    kwargs={"nws_user_agent":os.getenv("NWS_USER_AGENT","prediction-market-research/0.1")}
    if args.smoke:
        payload=_daily_payload(run_today(persist=False,**kwargs))
    else:
        cycle=run_operational_cycle(persist=True,**kwargs)
        payload=_daily_payload(cycle.daily)
        payload.update({
            "resolutions_checked":cycle.resolutions_checked,
            "resolutions_completed":cycle.resolutions_completed,
        })
    print(json.dumps(payload,indent=2))

if __name__=="__main__":
    main()
