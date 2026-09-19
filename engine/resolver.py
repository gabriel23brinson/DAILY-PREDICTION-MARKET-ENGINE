from __future__ import annotations
import os
from datetime import datetime, timezone
import psycopg
from .kalshi import KalshiPublicClient
from .resolution import score_resolution

FINAL={"yes":"YES","no":"NO","void":"VOID"}

def normalize_result(market: dict) -> str | None:
    raw=str(market.get("result") or "").strip().lower()
    return FINAL.get(raw)

def resolve_pending(dsn: str | None=None, client: KalshiPublicClient | None=None) -> dict[str,int]:
    dsn=dsn or os.environ["SUPABASE_DATABASE_URL"]
    client=client or KalshiPublicClient()
    checked=resolved=0
    with psycopg.connect(dsn) as con:
        with con.cursor() as cur:
            cur.execute("""select id,ticker,raw_model_probability from public.predictions
                           where resolved=false and decision='PAPER' order by created_at""")
            rows=cur.fetchall()
            for prediction_id,ticker,p in rows:
                checked+=1
                wrapper=client.get_market(ticker)
                market=wrapper.get("market",wrapper)
                outcome=normalize_result(market)
                if not outcome: continue
                score=score_resolution(float(p),outcome)
                cur.execute("""update public.predictions set resolved=true,outcome=%s,resolved_at=%s,
                               brier_score=%s,log_loss=%s where id=%s and resolved=false""",
                            (outcome,datetime.now(timezone.utc),score.brier_score,score.log_loss,prediction_id))
                resolved+=cur.rowcount
        con.commit()
    return {"checked":checked,"resolved":resolved}
