from __future__ import annotations
import json, os
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
import psycopg
from psycopg.types.json import Jsonb
from .research import ResearchResult
from .evidence import EvidenceBundle

class Ledger:
    def __init__(self, dsn: str | None=None):
        self.dsn=dsn or os.environ["SUPABASE_DATABASE_URL"]

    def record(self, *, market: dict, result: ResearchResult, evidence: EvidenceBundle,
               model_name: str="weather_baseline", model_version: str="0.1.0") -> int:
        with psycopg.connect(self.dsn) as con:
            with con.cursor() as cur:
                cur.execute("""insert into public.markets
                (ticker,event_ticker,category,title,subtitle,close_time,expected_expiration_time,
                 yes_bid,yes_ask,no_bid,no_ask,volume,open_interest,rules_primary,raw_payload,last_seen_at)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())
                on conflict (ticker) do update set
                yes_bid=excluded.yes_bid,yes_ask=excluded.yes_ask,no_bid=excluded.no_bid,no_ask=excluded.no_ask,
                volume=excluded.volume,open_interest=excluded.open_interest,raw_payload=excluded.raw_payload,last_seen_at=now()""",
                (market.get("ticker"),market.get("event_ticker"),market.get("category") or "weather",
                 market.get("title") or market.get("ticker"),market.get("subtitle"),market.get("close_time"),
                 market.get("expected_expiration_time"),market.get("yes_bid"),market.get("yes_ask"),
                 market.get("no_bid"),market.get("no_ask"),market.get("volume"),market.get("open_interest"),
                 market.get("rules_primary"),Jsonb(market)))
                cur.execute("""insert into public.predictions
                (ticker,category,model_name,model_version,side,market_probability,raw_model_probability,
                 calibrated_probability,edge,decision,evidence)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id""",
                (result.ticker,market.get("category") or "weather",model_name,model_version,result.edge.side,
                 float(result.edge.entry_price),result.probability.probability,result.probability.probability,
                 float(result.edge.net_edge),result.edge.decision,Jsonb(result.diagnostics)))
                prediction_id=cur.fetchone()[0]
                for item in evidence.items:
                    cur.execute("""insert into public.evidence_snapshots
                    (prediction_id,ticker,provider,source_tier,endpoint,retrieved_at,observed_at,units,stale,critical,
                     payload_hash,value_json,metadata) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (prediction_id,result.ticker,item.provider,item.source_tier.value,item.endpoint,item.retrieved_at,
                     item.observed_at,item.units,item.stale,item.critical,item.payload_hash,Jsonb(item.value),Jsonb(item.metadata)))
            con.commit()
        return prediction_id
