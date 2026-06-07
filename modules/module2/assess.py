# modules/module2/assess.py
# Module 2 — Run Assessment page
# 5-dimension scoring form with sliders + live score preview + AI submission

import streamlit as st
import json
from datetime import datetime

from config.constants import ASSESSMENT_DIMENSIONS, VERDICT_CONFIG, REQUIRED_FIELDS
from config.prompts import M2_SYSTEM_PROMPT
from database.db import db_save_assessment, db_update_status, db_load_all
from utils.helpers import get_completeness_color, call_m2_ai

SCALE_LABELS = {
    1: "1 — Strongly disagree",
    2: "2 — Disagree",
    3: "3 — Neutral",
    4: "4 — Agree",
    5: "5 — Strongly agree",
}


def score_to_verdict(score: float) -> str:
    if score >= 3.5:
        return "Feasible"
    if score >= 2.5:
        return "Conditional"
    return "Not Feasible"


def render():
    st.markdown("""
    <div class="page-hdr">
      <h2>📋 Feasibility Assessment</h2>
      <p>Rate each dimension on a 1–5 scale. Different stakeholder groups own each section.</p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.m2_selected_id:
        st.warning("No problem selected. Go to **Select Problem** first.")
        return

    problem = next(
        (r for r in st.session_state.submitted_records
         if r["id"] == st.session_state.m2_selected_id), None
    )
    if not problem:
        st.error("Selected problem not found.")
        return

    # Problem context expander
    with st.expander("📌 Problem being assessed", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Reference:** `{problem['id']}`")
            st.markdown(f"**Problem:** {problem.get('problem_statement','')}")
            st.markdown(f"**Objective:** {problem.get('business_objective','')}")
            st.markdown(f"**Solution:** {problem.get('solution_approach','')}")
        with c2:
            st.markdown(f"**Owner:** {problem.get('action_owner','')}")
            st.markdown(f"**Timeline:** {problem.get('timeline','')}")
            st.markdown(f"**Workflow:** {problem.get('workflow_location','')}")
            st.markdown(f"**Value:** {problem.get('business_value','')}")

    # Assessor name
    st.markdown('<div class="scard">', unsafe_allow_html=True)
    assessor = st.text_input("Your name / assessor name", placeholder="e.g. Rahul Sharma",
                             key="m2_assessor")
    st.markdown("</div>", unsafe_allow_html=True)

    # Ensure responses dict exists
    if "m2_responses" not in st.session_state:
        st.session_state.m2_responses = {}

    # ── Dimension scoring ──────────────────────────────────────────────────────
    dim_scores = {}
    for dim in ASSESSMENT_DIMENSIONS:
        did = dim["id"]
        if did not in st.session_state.m2_responses:
            st.session_state.m2_responses[did] = {}

        st.markdown(f"""
        <div class="scard" style="border-left:4px solid {dim['color']};">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.3rem;">
            <span style="font-size:1.4rem;">{dim['icon']}</span>
            <div>
              <div style="font-weight:700;font-size:1rem;color:#1a1a2e;">{dim['label']}</div>
              <div style="font-size:0.75rem;color:#888;">Stakeholder: <strong>{dim['role']}</strong></div>
            </div>
          </div>
          <div style="font-size:0.82rem;color:#666;margin-bottom:1rem;">{dim['desc']}</div>
        </div>""", unsafe_allow_html=True)

        q_scores = []
        for q_id, q_label in dim["questions"]:
            cur_val = st.session_state.m2_responses[did].get(q_id, 3)
            val = st.select_slider(
                q_label, options=[1, 2, 3, 4, 5],
                value=cur_val,
                format_func=lambda x: SCALE_LABELS[x],
                key=f"m2_{did}_{q_id}"
            )
            st.session_state.m2_responses[did][q_id] = val
            q_scores.append(val)

        dim_avg = sum(q_scores) / len(q_scores)
        dim_scores[did] = round(dim_avg, 2)
        color = get_completeness_color(dim_avg / 5 * 100)
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    background:#f8f8fd;border-radius:8px;padding:0.5rem 0.9rem;margin:0.5rem 0 0.2rem;">
          <span style="font-size:0.8rem;color:#666;">Dimension score</span>
          <span style="font-weight:700;color:{color};font-size:1rem;">{dim_avg:.1f} / 5</span>
        </div>
        <hr style="border-color:#f0f0f8;margin:0.8rem 0;">""", unsafe_allow_html=True)

    # ── Overall score + verdict preview ───────────────────────────────────────
    overall = round(sum(dim_scores.values()) / len(dim_scores), 2)
    verdict = score_to_verdict(overall)
    vc      = VERDICT_CONFIG[verdict]
    pct     = int(overall / 5 * 100)

    st.markdown(f"""
    <div class="scard" style="border:2px solid {vc['color']};">
      <div style="font-weight:700;font-size:1rem;margin-bottom:0.8rem;">Overall Feasibility Score</div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="font-size:2rem;font-weight:800;color:{vc['color']};">
          {overall:.2f}<span style="font-size:1rem;color:#aaa;"> / 5</span>
        </span>
        <span style="background:{vc['bg']};color:{vc['color']};padding:6px 16px;
                     border-radius:20px;font-weight:700;font-size:1rem;">{vc['icon']} {verdict}</span>
      </div>
      <div style="background:#eee;border-radius:8px;height:10px;">
        <div style="background:{vc['color']};width:{pct}%;height:10px;border-radius:8px;transition:width 0.4s;"></div>
      </div>
      <div style="font-size:0.75rem;color:#aaa;margin-top:6px;">
        ≥3.5 = Feasible · 2.5–3.4 = Conditional · &lt;2.5 = Not Feasible
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Dimension breakdown summary ───────────────────────────────────────────
    st.markdown('<div class="scard">', unsafe_allow_html=True)
    st.markdown("**Score breakdown by dimension**")
    for dim in ASSESSMENT_DIMENSIONS:
        s     = dim_scores.get(dim["id"], 0)
        pct_d = int(s / 5 * 100)
        col   = get_completeness_color(pct_d)
        st.markdown(f"""
        <div style="margin-bottom:0.7rem;">
          <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:3px;">
            <span>{dim['icon']} {dim['label']}</span>
            <span style="font-weight:700;color:{col};">{s:.1f}/5</span>
          </div>
          <div style="background:#f0f0f8;border-radius:6px;height:7px;">
            <div style="background:{col};width:{pct_d}%;height:7px;border-radius:6px;"></div>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Submit ────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("🚀  Submit Assessment & Generate AI Recommendation",
                 type="primary", use_container_width=True):
        if not assessor:
            st.warning("Please enter your name before submitting.")
            return
        _submit_assessment(problem, dim_scores, overall, verdict, assessor)


def _submit_assessment(problem, dim_scores, overall, verdict, assessor):
    """Save assessment to DB and trigger AI recommendation."""
    prompt = _build_prompt(problem, dim_scores, overall, verdict)
    with st.spinner("Generating AI recommendation…"):
        ai_reco = call_m2_ai(prompt)

    rec_id = f"FA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    db_save_assessment({
        "id":                       rec_id,
        "problem_id":               st.session_state.m2_selected_id,
        "assessed_at":              datetime.now().strftime("%Y-%m-%d %H:%M"),
        "assessor_name":            assessor,
        "ai_suitability_score":     dim_scores.get("ai_suitability", 0),
        "economic_viability_score": dim_scores.get("economic_viability", 0),
        "data_readiness_score":     dim_scores.get("data_readiness", 0),
        "workflow_maturity_score":  dim_scores.get("workflow_maturity", 0),
        "change_management_score":  dim_scores.get("change_management", 0),
        "overall_score":            overall,
        "verdict":                  verdict,
        "ai_recommendation":        ai_reco,
        "responses":                json.dumps(st.session_state.m2_responses),
    })

    # Auto-update M1 problem status based on verdict
    new_status = {
        "Feasible":     "Under Review",
        "Conditional":  "Deferred",
        "Not Feasible": "Rejected",
    }.get(verdict, "Under Review")
    db_update_status(st.session_state.m2_selected_id, new_status)

    st.session_state.submitted_records = db_load_all()
    st.session_state.m2_scores         = dim_scores
    st.session_state.m2_submitted      = True
    st.session_state.m2_ai_reco        = ai_reco
    st.session_state.m2_sub            = "results"
    st.rerun()


def _build_prompt(problem, dim_scores, overall, verdict):
    """Build the full prompt for the M2 AI recommendation call."""
    dim_lines = []
    for dim in ASSESSMENT_DIMENSIONS:
        s = dim_scores.get(dim["id"], 0)
        dim_lines.append(f"  - {dim['label']} ({dim['role']}): {s:.1f}/5")
        for q_id, q_label in dim["questions"]:
            ans = st.session_state.m2_responses.get(dim["id"], {}).get(q_id, 0)
            dim_lines.append(f"      • {q_label}: {ans}/5")

    return f"""PROBLEM STATEMENT (from Module 1):
- Problem: {problem.get('problem_statement','')}
- Objective: {problem.get('business_objective','')}
- Solution approach: {problem.get('solution_approach','')}
- Business value: {problem.get('business_value','')}
- Workflow: {problem.get('workflow_location','')}
- Timeline: {problem.get('timeline','')}
- Owner: {problem.get('action_owner','')}

FEASIBILITY SCORES:
{chr(10).join(dim_lines)}

Overall weighted score: {overall:.2f}/5
Verdict: {verdict}

{M2_SYSTEM_PROMPT}"""
