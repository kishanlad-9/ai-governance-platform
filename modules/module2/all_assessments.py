# modules/module2/all_assessments.py
# Module 2 — All Assessments page
# Summary metrics + full table of every assessment ever run

import streamlit as st
import pandas as pd
from datetime import datetime

from config.constants import ASSESSMENT_DIMENSIONS, VERDICT_CONFIG
from database.db import db_load_assessments


def render():
    st.markdown("""
    <div class="page-hdr">
      <h2>🗂️ All Assessments</h2>
      <p>Complete history of all feasibility assessments across all problem statements.</p>
    </div>""", unsafe_allow_html=True)

    assessments = db_load_assessments()
    if not assessments:
        st.markdown("""
        <div class="coming-soon">
          <div style="font-size:2.5rem;margin-bottom:1rem;">📭</div>
          <h3>No assessments yet</h3>
          <p>Select a problem and run an assessment to see results here.</p>
        </div>""", unsafe_allow_html=True)
        return

    _render_metrics(assessments)
    _render_table(assessments)
    _render_export(assessments)


def _render_metrics(assessments):
    total     = len(assessments)
    feasible  = sum(1 for a in assessments if a["verdict"] == "Feasible")
    cond      = sum(1 for a in assessments if a["verdict"] == "Conditional")
    not_f     = sum(1 for a in assessments if a["verdict"] == "Not Feasible")
    avg_score = sum(a["overall_score"] for a in assessments) / total

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Assessments", total)
    m2.metric("✅ Feasible",        feasible)
    m3.metric("⚠️ Conditional",    cond)
    m4.metric("❌ Not Feasible",    not_f)
    m5.metric("Avg Score",          f"{avg_score:.2f}/5")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)


def _render_table(assessments):
    rows = []
    for a in assessments:
        rows.append({
            "Assessment ID": a["id"],
            "Problem ID":    a["problem_id"],
            "Assessed":      a["assessed_at"],
            "Assessor":      a["assessor_name"],
            "AI Suit.":      f"{a['ai_suitability_score']:.1f}",
            "Econ. Viab.":   f"{a['economic_viability_score']:.1f}",
            "Data Ready":    f"{a['data_readiness_score']:.1f}",
            "Workflow":      f"{a['workflow_maturity_score']:.1f}",
            "Change Mgmt":   f"{a['change_management_score']:.1f}",
            "Overall":       f"{a['overall_score']:.2f}",
            "Verdict":       a["verdict"],
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_export(assessments):
    csv = pd.DataFrame(assessments).to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Export All Assessments CSV", csv,
        f"all_assessments_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv", use_container_width=True
    )
