from __future__ import annotations

import os
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
    ("Scanned", "Supported", "Researched", "PAPER", "PASS", "Failed"),
    (run.scanned_same_day, run.supported, run.researched, run.paper, run.passed, len(run.failures)),
):
    col.metric(label, value)

rows = []
for item in run.ranked:
    research = item.result.research
    rows.append({
        "Ticker": item.market.get("ticker"),
        "Decision": item.result.status,
        "Model Probability": round(research.probability.probability * 100, 1),
        "Entry Price": float(research.edge.entry_price),
        "Net Edge": round(float(research.edge.net_edge) * 100, 1),
        "Reason": item.result.reason,
    })

st.subheader("Ranked Research")
if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.write("No researched candidates in this run.")

if run.early_passes:
    with st.expander("Early PASS reasons"):
        for item in run.early_passes:
            st.write(f"{item.ticker}: {item.reason}")

if run.failures:
    with st.expander("Failures"):
        for item in run.failures:
            st.write(f"{item.ticker}: {item.error}")

st.caption("Research software. PAPER decisions are model outputs, not executed trades.")
