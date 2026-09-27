from __future__ import annotations

import os
import re
import pandas as pd
import streamlit as st

from engine.run_today import run_today

st.set_page_config(page_title="Prediction Market Engine", page_icon="📈", layout="wide")
st.title("Prediction Market Engine")
st.caption("Live Kalshi research • PAPER only • no order execution")

if "daily_run" not in st.session_state:
    st.session_state.daily_run = None

if st.button("Run Live Scan", type="primary"):
    with st.spinner("Scanning and researching live same-day markets..."):
        try:
            st.session_state.daily_run = run_today(
                persist=False,
                nws_user_agent=os.getenv("NWS_USER_AGENT", "prediction-market-research/0.1"),
            )
        except Exception as exc:
            st.error(f"Scan failed: {type(exc).__name__}: {exc}")

run = st.session_state.daily_run
if run is None:
    st.info("Press Run Live Scan to research today's supported markets.")
    st.stop()

cols = st.columns(6)
for col, label, value in zip(
    cols,
    ("Scanned", "Supported", "Researched", "PAPER Candidates", "Passed", "Failed"),
    (run.scanned_same_day, run.supported, run.researched, run.paper, run.passed, len(run.failures)),
):
    col.metric(label, value)

if run.paper:
    st.success(f"{run.paper} market(s) cleared the current PAPER threshold.")
else:
    st.info("No market cleared the PAPER threshold in this scan. PASS means the engine did not find a qualifying edge.")

def readable_market(market: dict) -> str:
    title = str(market.get("title") or "").strip()
    subtitle = str(market.get("subtitle") or "").strip()
    if title and title != market.get("ticker"):
        return f"{title} — {subtitle}" if subtitle and subtitle not in title else title
    return str(market.get("ticker") or "Unknown market")

def pct(value: float) -> str:
    return f"{value * 100:.1f}%"

st.subheader("Research Results")
for item in run.ranked:
    research = item.result.research
    edge = research.edge
    decision = item.result.status
    icon = "🟢" if decision == "PAPER" else "🔴"
    name = readable_market(item.market)
    with st.container(border=True):
        st.markdown(f"### {icon} {name}")
        a,b,c,d = st.columns(4)
        a.metric("Engine YES probability", pct(research.probability.probability))
        valid_price = 0 < float(edge.entry_price) < 1
        b.metric("Market entry price", pct(float(edge.entry_price)) if valid_price else "Unavailable")
        c.metric("Net edge", pct(float(edge.net_edge)) if valid_price else "Unavailable")
        d.metric("Decision", decision)
        reason = item.result.reason.replace("_", " ").strip().capitalize()
        st.write(f"**Why:** {reason}.")
        with st.expander("Technical details"):
            st.write(f"Ticker: {item.market.get('ticker')}")
            st.write(f"Raw entry price: {edge.entry_price}")
            st.write(f"Model diagnostics: {research.diagnostics}")

if run.early_passes:
    with st.expander("Markets passed before modeling"):
        for item in run.early_passes:
            st.write(f"{item.ticker}: {item.reason}")

if run.failures:
    with st.expander("Technical failures"):
        for item in run.failures:
            st.write(f"{item.ticker}: {item.error}")

st.caption("Research software. PAPER decisions are model outputs, not executed trades.")
