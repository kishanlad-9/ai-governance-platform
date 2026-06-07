# modules/module2/results.py
# Module 2 — Assessment Results page
# Shows verdict, dimension breakdown, score chart, problem context, AI report

import streamlit as st
import pandas as pd

from config.constants import ASSESSMENT_DIMENSIONS, VERDICT_CONFIG, REQUIRED_FIELDS
from database.db import db_load_assessments
from utils.helpers import get_completeness_color


def render():
    st.markdown("""
    <div class="page-hdr">
      <h2>📊 Assessment Results</h2>
      <p>Full feasibility verdict, dimension breakdown, and AI-generated recommendation report.</p>
    </div>""", unsafe_allow_html=True)

    pid = st.session_state.m2_selected_id
    if not pid:
        st.info("No assessment selected. Run an assessment first.")
        return

    assessments = db_load_assessments(pid)
    if not assessments:
        st.info("No assessment found for this problem. Go to **Run Assessment**.")
        return

    latest  = assessments[0]
    verdict = latest["verdict"]
    vc      = VERDICT_CONFIG.get(verdict, VERDICT_CONFIG["Conditional"])
    overall = latest["overall_score"]
    pct     = int(overall / 5 * 100)
    problem = next((r for r in st.session_state.submitted_records if r["id"] == pid), {})

    _render_header(latest, pid, vc, overall, pct)

    col_sc, col_prob = st.columns([1.1, 0.9], gap="large")
    with col_sc:
        _render_scores(latest, vc)
    with col_prob:
        _render_problem_context(problem)

    _render_ai_report(latest)
    _render_export(latest, pid)


def _render_header(latest, pid, vc, overall, pct):
    st.markdown(f"""
    <div class="scard" style="border:2px solid {vc['color']};">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
        <div>
          <div style="font-size:0.72rem;color:#aaa;font-weight:700;letter-spacing:0.08em;">ASSESSMENT REFERENCE</div>
          <div style="font-family:monospace;font-size:1rem;color:#6C63FF;font-weight:700;margin:2px 0;">{latest['id']}</div>
          <div style="font-size:0.75rem;color:#888;">
            Problem: {pid} · Assessed: {latest['assessed_at']} · By: {latest['assessor_name']}
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:2.2rem;font-weight:800;color:{vc['color']};">
            {overall:.2f}<span style="font-size:1rem;color:#ccc;">/5</span>
          </div>
          <span style="background:{vc['bg']};color:{vc['color']};padding:5px 14px;border-radius:20px;font-weight:700;">
            {vc['icon']} {latest['verdict']}
          </span>
        </div>
      </div>
      <div style="background:#f0f0f8;border-radius:8px;height:10px;margin-top:1rem;">
        <div style="background:{vc['color']};width:{pct}%;height:10px;border-radius:8px;"></div>
      </div>
    </div>""", unsafe_allow_html=True)


def _render_scores(latest, vc):
    dim_score_map = {
        "ai_suitability":     latest["ai_suitability_score"],
        "economic_viability": latest["economic_viability_score"],
        "data_readiness":     latest["data_readiness_score"],
        "workflow_maturity":  latest["workflow_maturity_score"],
        "change_management":  latest["change_management_score"],
    }

    st.markdown('<div class="scard">', unsafe_allow_html=True)
    st.markdown("**Dimension Scores**")
    for dim in ASSESSMENT_DIMENSIONS:
        s     = dim_score_map.get(dim["id"], 0)
        pct_d = int(s / 5 * 100)
        col   = get_completeness_color(pct_d)
        st.markdown(f"""
        <div style="margin-bottom:0.85rem;">
          <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:4px;">
            <span>{dim['icon']} <strong>{dim['label']}</strong>
              <span style="color:#aaa;font-size:0.72rem;"> ({dim['role']})</span>
            </span>
            <span style="font-weight:700;color:{col};">{s:.1f}/5</span>
          </div>
          <div style="background:#f0f0f8;border-radius:6px;height:8px;">
            <div style="background:{col};width:{pct_d}%;height:8px;border-radius:6px;"></div>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Score chart
    df_scores = pd.DataFrame({
        "Dimension": [d["label"] for d in ASSESSMENT_DIMENSIONS],
        "Score":     [dim_score_map.get(d["id"], 0) for d in ASSESSMENT_DIMENSIONS],
    })
    st.markdown('<div class="scard">', unsafe_allow_html=True)
    st.markdown("**Score chart**")
    st.bar_chart(df_scores.set_index("Dimension"), color="#6C63FF")
    st.markdown("</div>", unsafe_allow_html=True)


def _render_problem_context(problem):
    st.markdown('<div class="scard">', unsafe_allow_html=True)
    st.markdown("**Problem context**")
    for key, label in REQUIRED_FIELDS:
        val = problem.get(key, "—") or "—"
        st.markdown(f"""
        <div class="fcard done" style="margin-bottom:0.4rem;">
          <div class="fcard-lbl done">{label}</div>
          <div class="fcard-val">{val}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_ai_report(latest):
    ai_reco = latest.get("ai_recommendation", "")
    if not ai_reco:
        return
    st.markdown('<div class="scard" style="border-left:4px solid #6C63FF;">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Recommendation Report")
    st.markdown(ai_reco)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_export(latest, pid):
    df_exp = pd.DataFrame([{
        "Assessment ID":      latest["id"],
        "Problem ID":         pid,
        "Assessed at":        latest["assessed_at"],
        "Assessor":           latest["assessor_name"],
        "AI Suitability":     latest["ai_suitability_score"],
        "Economic Viability": latest["economic_viability_score"],
        "Data Readiness":     latest["data_readiness_score"],
        "Workflow Maturity":  latest["workflow_maturity_score"],
        "Change Management":  latest["change_management_score"],
        "Overall Score":      latest["overall_score"],
        "Verdict":            latest["verdict"],
    }])
    csv = df_exp.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Results CSV", csv,
        f"feasibility_{latest['id']}.csv",
        "text/csv", use_container_width=True
    )
