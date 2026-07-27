"""Blinkit Discovery Engine — Case 1 Streamlit dashboard."""

from __future__ import annotations

import os

import requests
import streamlit as st

API_BASE = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def api_get(path: str):
    r = requests.get(f"{API_BASE}{path}", timeout=30)
    r.raise_for_status()
    return r.json()


def api_post(path: str, json: dict | None = None):
    r = requests.post(f"{API_BASE}{path}", json=json or {}, timeout=60)
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        st.error(f"API error {r.status_code}: {detail}")
        return None
    return r.json()


st.set_page_config(page_title="Blinkit Discovery", layout="wide")
st.title("Blinkit Discovery Engine")
st.caption(f"Backend: `{API_BASE}`")

tab_overview, tab_mvp, tab_insights = st.tabs(["Overview", "MVP demo", "Insights"])

with tab_overview:
    try:
        health = api_get("/api/health")
        stats = api_get("/api/reviews/stats")
        analysis = api_get("/api/pipeline/analysis-status")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Health", health.get("status", "—"))
        c2.metric("Reviews", stats.get("total_reviews", 0))
        c3.metric("Themes", analysis.get("themes", 0))
        c4.metric("Insights", analysis.get("insights", 0))
    except requests.RequestException as exc:
        st.error(f"Cannot reach API: {exc}")

    if st.button("Seed research data"):
        out = api_post("/api/research/seed?code=true")
        if out:
            st.success(
                f"Loaded {out.get('interviews_loaded')} interviews, "
                f"{out.get('survey_rows_loaded')} survey rows"
            )

with tab_mvp:
    status = api_get("/api/mvp/status")
    if not status.get("ready"):
        st.warning("Generate insights on the backend before running MVP recommend.")
    segment = st.selectbox(
        "Customer segment",
        ["mission_shopper", "student", "family_stockup", "explorer", "new_parent", "pet_owner"],
    )
    default_basket = "Amul Taaza Milk 1L\nBritannia Brown Bread"
    basket_text = st.text_area("Basket (one item per line)", default_basket, height=120)
    presets = api_get("/api/mvp/eval-baskets")
    if presets:
        choice = st.selectbox("Load preset", ["—"] + [p["id"] for p in presets])
        if choice != "—":
            p = next(x for x in presets if x["id"] == choice)
            segment = p["customer_segment"]
            basket_text = "\n".join(i["name"] for i in p["items"])

    if st.button("Get suggestion", disabled=not status.get("ready")):
        items = [{"name": line.strip()} for line in basket_text.splitlines() if line.strip()]
        body = {"basket_items": items, "customer_segment": segment, "limit": 1}
        out = api_post("/api/mvp/recommend", body)
        if out and out.get("suggestions"):
            s = out["suggestions"][0]
            st.subheader(s["product_name"])
            st.write(
                f"**Category:** {s['category']} · **Barrier:** {s['dominant_barrier']} · "
                f"**Insight #{s['insight_id']}**"
            )
            st.info(s["message"])

    if st.button("Run evaluation harness"):
        ev = api_post("/api/mvp/evaluate", {"limit": 1})
        if ev:
            sm = ev["summary"]
            st.write(
                f"Pass rate **{sm['pass_rate']*100:.0f}%** · "
                f"{sm['passed_cases']}/{sm['total_cases']} cases"
            )

with tab_insights:
    try:
        rows = api_get("/api/insights?limit=15")
        if not rows:
            st.info("No insights yet.")
        for row in rows:
            with st.expander(f"#{row['id']} — {row['problem'][:80]}…"):
                st.write(row.get("evidence") or "")
                st.caption(f"Status: {row.get('validation_status')} · confidence {row.get('confidence_score')}")
    except requests.RequestException as exc:
        st.error(str(exc))
