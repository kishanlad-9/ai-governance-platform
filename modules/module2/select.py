# modules/module2/select.py
# Module 2 — AI-driven feasibility assessment, step-by-step
# Step 1: Pick a problem
# Step 2: AI analyses and scores automatically
# Step 3: Results with verdict, scores, report
# Step 4: Done

import streamlit as st
import json
import pandas as pd
from datetime import datetime

from config.constants import ASSESSMENT_DIMENSIONS, VERDICT_CONFIG, STATUS_BADGE
from database.db import db_save_assessment, db_update_status, db_load_all, db_load_assessments
from utils.helpers import get_completeness_color, call_m2_assessment


def verdict_from_score(s):
    return "Feasible" if s >= 3.5 else "Conditional" if s >= 2.5 else "Not Feasible"


def render():
    step = st.session_state.get("m2_step", "pick")
    if   step == "pick":    _step_pick()
    elif step == "analyse": _step_analyse()
    elif step == "results": _step_results()
    elif step == "done":    _step_done()


# ── Step 1: Pick a problem ────────────────────────────────────────────────────
def _step_pick():
    st.markdown("""
    <div class="step-hdr">
      <h1>Feasibility Assessment</h1>
      <p>Select a problem statement for the AI to assess.</p>
    </div>""", unsafe_allow_html=True)

    records = st.session_state.submitted_records
    if not records:
        st.markdown("""<div class="coming-wrap">
          <div style="font-size:2.5rem">📭</div>
          <h2>No problems submitted yet</h2>
          <p style="font-size:0.85rem">Go to Problem Definition and submit a use case first.</p>
        </div>""", unsafe_allow_html=True)
        return

    for r in records:
        sel = st.session_state.get("m2_selected_id") == r["id"]
        sc  = STATUS_BADGE.get(r.get("status", ""), "b-submitted")
        bg  = "#F3F1FF" if sel else "#fff"
        bdr = "2px solid #6C63FF" if sel else "1px solid #EAEBF5"

        st.markdown(f"""
        <div style="background:{bg};border:{bdr};border-radius:12px;
                    padding:1rem 1.2rem;margin-bottom:0.6rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
            <span style="font-family:monospace;font-size:0.78rem;color:#6C63FF;font-weight:700;">{r['id']}</span>
            <span class="badge {sc}">{r.get('status','')}</span>
          </div>
          <div style="font-size:0.92rem;color:#1a1a2e;font-weight:500;margin-bottom:0.2rem;">
            {r.get('problem_statement','')[:100]}…
          </div>
          <div style="font-size:0.75rem;color:#aaa;">
            {r.get('action_owner','—')} · {r.get('submitted_at','—')}
          </div>
        </div>""", unsafe_allow_html=True)

        label = "✓ Selected" if sel else "Select"
        if st.button(label, key=f"pick_{r['id']}", use_container_width=True,
                     type="primary" if sel else "secondary"):
            st.session_state.m2_selected_id  = r["id"]
            st.session_state.m2_ai_result    = None
            st.rerun()

    if st.session_state.get("m2_selected_id"):
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("Run AI Assessment →", type="primary", use_container_width=True):
            st.session_state.m2_step = "analyse"
            st.rerun()


# ── Step 2: AI analyses the problem ──────────────────────────────────────────
def _step_analyse():
    st.markdown("""
    <div class="step-hdr">
      <h1>AI Analysis</h1>
      <p>Gemini is evaluating the problem across 5 feasibility dimensions.</p>
    </div>""", unsafe_allow_html=True)

    # If already computed (rerun guard), skip straight to save
    if st.session_state.get("m2_ai_result"):
        _save_and_advance()
        return

    pid     = st.session_state.get("m2_selected_id")
    problem = next((r for r in st.session_state.submitted_records if r["id"] == pid), None)
    if not problem:
        st.error("Problem not found.")
        return

    # Show what's being assessed
    st.markdown(f"""
    <div style="background:#F7F8FC;border:1px solid #EAEBF5;border-radius:12px;
                padding:1rem 1.3rem;margin-bottom:1.5rem;">
      <div style="font-size:0.7rem;color:#aaa;font-weight:700;letter-spacing:0.08em;margin-bottom:0.4rem;">ANALYSING</div>
      <div style="font-size:0.95rem;color:#1a1a2e;font-weight:500;">{problem.get('problem_statement','')}</div>
      <div style="font-size:0.78rem;color:#888;margin-top:0.3rem;">
        {problem.get('workflow_location','—')} · {problem.get('action_owner','—')}
      </div>
    </div>""", unsafe_allow_html=True)

    # Dimension list so user sees what AI will evaluate
    st.markdown("<div style='margin-bottom:1.2rem;'>", unsafe_allow_html=True)
    for dim in ASSESSMENT_DIMENSIONS:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:0.5rem 0;
                    border-bottom:1px solid #F0F0F8;font-size:0.88rem;color:#555;">
          <span style="font-size:1.1rem;">{dim['icon']}</span>
          <span>{dim['label']}</span>
          <span style="margin-left:auto;font-size:0.75rem;color:#aaa;">{dim['role']}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.spinner("AI is evaluating feasibility…"):
        result = call_m2_assessment(problem)

    if result:
        st.session_state.m2_ai_result = result
        _save_and_advance()
    else:
        st.error("Assessment failed. Please check your API key and try again.")
        if st.button("← Back", use_container_width=True):
            st.session_state.m2_step = "pick"
            st.rerun()


# ── Save to DB and go to results ──────────────────────────────────────────────
def _save_and_advance():
    result  = st.session_state.m2_ai_result
    pid     = st.session_state.m2_selected_id
    scores  = result.get("scores", {})
    overall = result.get("overall", 0.0)
    verdict = result.get("verdict", verdict_from_score(overall))

    # Build readable AI report from structured result
    strengths     = "\n".join(f"- {s}" for s in result.get("strengths", []))
    risks         = "\n".join(f"- {r}" for r in result.get("risks", []))
    recommendations = "\n".join(f"- {r}" for r in result.get("recommendations", []))
    dim_reasoning = result.get("dimension_reasoning", {})
    reasoning_md  = "\n".join(
        f"**{dim['label']}** ({scores.get(dim['id'], 0):.1f}/5): {dim_reasoning.get(dim['id'], '')}"
        for dim in ASSESSMENT_DIMENSIONS
    )

    ai_report = f"""## Overall Assessment\n{result.get('overall_summary', '')}\n\n## Dimension Breakdown\n{reasoning_md}\n\n## Strengths\n{strengths}\n\n## Risks & Gaps\n{risks}\n\n## Recommendations\n{recommendations}"""

    rec_id = f"FA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    db_save_assessment({
        "id":                       rec_id,
        "problem_id":               pid,
        "assessed_at":              datetime.now().strftime("%Y-%m-%d %H:%M"),
        "assessor_name":            "Gemini AI",
        "ai_suitability_score":     scores.get("ai_suitability", 0),
        "economic_viability_score": scores.get("economic_viability", 0),
        "data_readiness_score":     scores.get("data_readiness", 0),
        "workflow_maturity_score":  scores.get("workflow_maturity", 0),
        "change_management_score":  scores.get("change_management", 0),
        "risk_compliance_score":    scores.get("risk_compliance", 0),
        "hard_gate_triggered":      1 if result.get("hard_gate_triggered") else 0,
        "hard_gate_reason":         result.get("hard_gate_reason", ""),
        "overall_score":            overall,
        "verdict":                  verdict,
        "ai_recommendation":        ai_report,
        "responses":                json.dumps(scores),
    })

    new_status = {"Feasible": "Under Review", "Conditional": "Deferred",
                  "Not Feasible": "Rejected"}.get(verdict, "Under Review")
    db_update_status(pid, new_status)
    st.session_state.submitted_records = db_load_all()
    st.session_state.m2_step           = "results"
    st.rerun()


# ── Step 3: Results ───────────────────────────────────────────────────────────
def _step_results():
    pid         = st.session_state.get("m2_selected_id")
    assessments = db_load_assessments(pid)
    if not assessments:
        st.warning("No results found.")
        return

    latest           = assessments[0]
    verdict          = latest["verdict"]
    vc               = VERDICT_CONFIG.get(verdict, VERDICT_CONFIG["Conditional"])
    overall          = latest["overall_score"]
    result           = st.session_state.get("m2_ai_result", {}) or {}
    hard_gate        = latest.get("hard_gate_triggered", 0)
    hard_gate_reason = latest.get("hard_gate_reason", "") or ""
    dim_map = {
        "ai_suitability":     latest["ai_suitability_score"],
        "economic_viability": latest["economic_viability_score"],
        "data_readiness":     latest["data_readiness_score"],
        "workflow_maturity":  latest["workflow_maturity_score"],
        "change_management":  latest["change_management_score"],
        "risk_compliance":    latest.get("risk_compliance_score", 0),
    }
    dim_reasoning = result.get("dimension_reasoning", {})

    st.markdown(f"""
    <div class="step-hdr">
      <h1>Assessment Results</h1>
      <p>{latest['id']} · {latest['assessed_at']} · Assessed by {latest['assessor_name']}</p>
    </div>""", unsafe_allow_html=True)

    # Verdict card
    st.markdown(f"""
    <div style="background:{vc['bg']};border:1.5px solid {vc['color']};border-radius:14px;
                padding:1.2rem 1.6rem;margin-bottom:1.5rem;
                display:flex;justify-content:space-between;align-items:center;">
      <div>
        <div style="font-size:0.7rem;color:{vc['color']};font-weight:700;letter-spacing:0.08em;">OVERALL VERDICT</div>
        <div style="font-size:1.9rem;font-weight:800;color:{vc['color']};margin-top:2px;">{overall:.2f}<span style="font-size:1rem;color:{vc['color']};opacity:0.6;"> / 5</span></div>
      </div>
      <div style="font-size:1rem;font-weight:700;color:{vc['color']};">{vc['icon']} {verdict}</div>
    </div>""", unsafe_allow_html=True)

    # Hard gate warning
    if hard_gate:
        st.error(f"🚫 Hard Gate Triggered: {hard_gate_reason}")

    # Overall summary
    if result.get("overall_summary"):
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #EAEBF5;border-radius:12px;
                    padding:1rem 1.3rem;margin-bottom:1.2rem;font-size:0.9rem;color:#444;line-height:1.6;">
          {result['overall_summary']}
        </div>""", unsafe_allow_html=True)

    for dim in ASSESSMENT_DIMENSIONS:
        s   = dim_map.get(dim["id"], 0)
        pct = int(s / 5 * 100)
        col = get_completeness_color(pct)
        reasoning = dim_reasoning.get(dim["id"], "")
        st.markdown(f"""
        <div class="score-row">
          <div class="s-label">
            <span>{dim['icon']} {dim['label']}</span>
            <span style="font-weight:700;color:{col};">{s:.1f}/5</span>
          </div>
          <div class="score-bar-bg">
            <div class="score-bar-fill" style="background:{col};width:{pct}%;"></div>
          </div>
          {f'<div style="font-size:0.78rem;color:#888;margin-top:4px;">{reasoning}</div>' if reasoning else ''}
        </div>""", unsafe_allow_html=True)

    # Full report
    ai_reco = latest.get("ai_recommendation", "")
    if ai_reco:
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        with st.expander("Full AI Report", expanded=False):
            st.markdown(ai_reco)

    # Export
    df = pd.DataFrame([{
        "Assessment ID":    latest["id"],
        "Problem ID":       pid,
        "Assessed at":      latest["assessed_at"],
        "Assessed by":      latest["assessor_name"],
        "Overall Score":    overall,
        "Verdict":          verdict,
        "Hard Gate":        "Yes" if hard_gate else "No",
        "Hard Gate Reason": hard_gate_reason,
        **{d["label"]: dim_map.get(d["id"]) for d in ASSESSMENT_DIMENSIONS},
    }])
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(),
                       f"assessment_{latest['id']}.csv", "text/csv",
                       use_container_width=True)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("Done →", type="primary", use_container_width=True):
        st.session_state.m2_step = "done"
        st.rerun()


# ── Step 4: Done ──────────────────────────────────────────────────────────────
def _step_done():
    pid         = st.session_state.get("m2_selected_id", "")
    assessments = db_load_assessments(pid)
    verdict     = assessments[0]["verdict"] if assessments else "—"
    badge_cls   = {"Feasible": "b-approved", "Conditional": "b-review",
                   "Not Feasible": "b-rejected"}.get(verdict, "b-submitted")

    st.markdown("""
    <div class="step-hdr">
      <h1>Assessment Complete</h1>
      <p>The AI feasibility assessment has been recorded.</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ref-wrap">
      <div>
        <div class="ref-meta">Problem ID</div>
        <div class="ref-id">{pid}</div>
      </div>
      <div style="text-align:right;">
        <div class="ref-meta">AI Verdict</div>
        <span class="badge {badge_cls}">{verdict}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    st.info("Proceed to **Gain–Pain Analysis** in Module 3.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Assess another", use_container_width=True):
            st.session_state.m2_step        = "pick"
            st.session_state.m2_selected_id = None
            st.session_state.m2_ai_result   = None
            st.rerun()
    with col2:
        if st.button("Go to Module 3 →", type="primary", use_container_width=True):
            st.session_state.active_module = "m3"
            st.rerun()
