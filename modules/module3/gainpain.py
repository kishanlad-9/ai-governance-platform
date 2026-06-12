# modules/module3/gainpain.py
# Module 3 — Gain Pain Analysis (NIST AI RMF)
# Step 1: Select problem + assessment
# Step 2: AI runs gain-pain analysis automatically
# Step 3: Results — gains vs pains, priority score, chart
# Step 4: Done

import streamlit as st
import json
import pandas as pd
from datetime import datetime

from config.constants import (
    GAIN_DIMENSIONS, PAIN_DIMENSIONS, PRIORITY_BANDS,
    STATUS_BADGE, REQUIRED_FIELDS
)
from config.prompts import M3_GAINPAIN_PROMPT
from database.db import (
    db_load_assessments, db_save_gainpain,
    db_load_gainpain, db_update_status, db_load_all
)
from utils.helpers import call_ai, clean_llm_json, get_completeness_color


def render():
    step = st.session_state.get("m3_step", "pick")
    if   step == "pick":    _step_pick()
    elif step == "analyse": _step_analyse()
    elif step == "results": _step_results()
    elif step == "done":    _step_done()


# ── Step 1: Select problem ────────────────────────────────────────────────────
def _step_pick():
    st.markdown("""
    <div class="step-hdr">
      <h1>Gain–Pain Analysis</h1>
      <p>Select a feasibility-assessed problem to run the NIST AI RMF gain-pain analysis.</p>
    </div>""", unsafe_allow_html=True)

    # Only show problems that have been assessed
    all_records  = st.session_state.submitted_records
    assessed_ids = {a["problem_id"] for a in db_load_assessments()}
    records      = [r for r in all_records if r["id"] in assessed_ids]

    if not records:
        st.markdown("""<div class="coming-wrap">
          <div style="font-size:2.5rem">📭</div>
          <h2>No assessed problems found</h2>
          <p style="font-size:0.85rem">Complete Module 2 — Feasibility Assessment first.</p>
        </div>""", unsafe_allow_html=True)
        return

    for r in records:
        sel      = st.session_state.get("m3_selected_id") == r["id"]
        sc       = STATUS_BADGE.get(r.get("status", ""), "b-submitted")
        bg       = "#F3F1FF" if sel else "#fff"
        bdr      = "2px solid #6C63FF" if sel else "1px solid #EAEBF5"
        assessments = db_load_assessments(r["id"])
        verdict  = assessments[0]["verdict"] if assessments else "—"
        vc_map   = {"Feasible": "#1D9E75", "Conditional": "#C07A10", "Not Feasible": "#C0392B"}
        vc_col   = vc_map.get(verdict, "#888")

        st.markdown(f"""
        <div style="background:{bg};border:{bdr};border-radius:12px;
                    padding:1rem 1.2rem;margin-bottom:0.6rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
            <span style="font-family:monospace;font-size:0.78rem;color:#6C63FF;font-weight:700;">{r['id']}</span>
            <div style="display:flex;gap:8px;align-items:center;">
              <span style="font-size:0.75rem;font-weight:700;color:{vc_col};">M2: {verdict}</span>
              <span class="badge {sc}">{r.get('status','')}</span>
            </div>
          </div>
          <div style="font-size:0.92rem;color:#1a1a2e;font-weight:500;margin-bottom:0.2rem;">
            {r.get('problem_statement','')[:95]}…
          </div>
          <div style="font-size:0.75rem;color:#aaa;">
            {r.get('action_owner','—')} · {r.get('submitted_at','—')}
          </div>
        </div>""", unsafe_allow_html=True)

        label = "✓ Selected" if sel else "Select"
        if st.button(label, key=f"m3pick_{r['id']}", use_container_width=True,
                     type="primary" if sel else "secondary"):
            st.session_state.m3_selected_id = r["id"]
            st.session_state.m3_ai_result   = None
            st.rerun()

    if st.session_state.get("m3_selected_id"):
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("Run Gain–Pain Analysis →", type="primary", use_container_width=True):
            st.session_state.m3_step = "analyse"
            st.rerun()


# ── Step 2: AI analyses ───────────────────────────────────────────────────────
def _step_analyse():
    st.markdown("""
    <div class="step-hdr">
      <h1>AI Analysis</h1>
      <p>Running NIST AI RMF gain-pain evaluation across 8 dimensions.</p>
    </div>""", unsafe_allow_html=True)

    if st.session_state.get("m3_ai_result"):
        _save_and_advance()
        return

    pid     = st.session_state.get("m3_selected_id")
    problem = next((r for r in st.session_state.submitted_records if r["id"] == pid), None)
    assessments = db_load_assessments(pid)
    assessment  = assessments[0] if assessments else {}

    if not problem:
        st.error("Problem not found.")
        return

    # Show what's being analysed
    st.markdown(f"""
    <div style="background:#FAFAFE;border:1px solid #EAEBF5;border-radius:12px;
                padding:1rem 1.3rem;margin-bottom:1.5rem;">
      <div style="font-size:0.7rem;color:#aaa;font-weight:700;letter-spacing:0.08em;margin-bottom:0.4rem;">ANALYSING</div>
      <div style="font-size:0.95rem;color:#1a1a2e;font-weight:500;">{problem.get('problem_statement','')}</div>
      <div style="font-size:0.78rem;color:#888;margin-top:0.3rem;">
        M2 Verdict: <strong>{assessment.get('verdict','—')}</strong> ·
        Score: <strong>{assessment.get('overall_score',0):.2f}/5</strong>
      </div>
    </div>""", unsafe_allow_html=True)

    # Show dimensions being evaluated
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📈 Gains being evaluated**")
        for d in GAIN_DIMENSIONS:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;padding:0.4rem 0;
                        border-bottom:1px solid #F0F0F8;font-size:0.85rem;color:#444;">
              <span>{d['icon']}</span>
              <span>{d['label']}</span>
              <span style="margin-left:auto;font-size:0.7rem;color:#aaa;font-weight:600;">{d['nist']}</span>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("**📉 Pains being evaluated**")
        for d in PAIN_DIMENSIONS:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;padding:0.4rem 0;
                        border-bottom:1px solid #F0F0F8;font-size:0.85rem;color:#444;">
              <span>{d['icon']}</span>
              <span>{d['label']}</span>
              <span style="margin-left:auto;font-size:0.7rem;color:#aaa;font-weight:600;">{d['nist']}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    with st.spinner("AI is running gain-pain analysis…"):
        result = _call_m3_ai(problem, assessment)

    if result:
        st.session_state.m3_ai_result = result
        _save_and_advance()
    else:
        st.error("Analysis failed. Check your API key and try again.")
        if st.button("← Back"):
            st.session_state.m3_step = "pick"
            st.rerun()


# ── Save to DB and advance ────────────────────────────────────────────────────
def _save_and_advance():
    result      = st.session_state.m3_ai_result
    pid         = st.session_state.m3_selected_id
    assessments = db_load_assessments(pid)
    aid         = assessments[0]["id"] if assessments else ""

    gains = result.get("gains", {})
    pains = result.get("pains", {})

    rec_id = f"GP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    db_save_gainpain({
        "id":                    rec_id,
        "problem_id":            pid,
        "assessment_id":         aid,
        "analysed_at":           datetime.now().strftime("%Y-%m-%d %H:%M"),
        "business_value_gain":   gains.get("business_value_gain", 0),
        "strategic_alignment":   gains.get("strategic_alignment", 0),
        "efficiency_gain":       gains.get("efficiency_gain", 0),
        "innovation_potential":  gains.get("innovation_potential", 0),
        "implementation_cost":   pains.get("implementation_cost", 0),
        "operational_risk":      pains.get("operational_risk", 0),
        "adoption_resistance":   pains.get("adoption_resistance", 0),
        "compliance_burden":     pains.get("compliance_burden", 0),
        "avg_gains":             result.get("avg_gains", 0),
        "avg_pains":             result.get("avg_pains", 0),
        "priority_score":        result.get("priority_score", 0),
        "priority_score_scaled": result.get("priority_score_scaled", 0),
        "priority_band":         result.get("priority_band", ""),
        "ai_analysis":           json.dumps(result),
    })

    # Update problem status based on priority
    band = result.get("priority_band", "")
    new_status = {
        "High Priority":   "Approved",
        "Medium Priority": "Under Review",
        "Low Priority":    "Deferred",
    }.get(band, "Under Review")
    db_update_status(pid, new_status)
    st.session_state.submitted_records = db_load_all()
    st.session_state.m3_step           = "results"
    st.rerun()


# ── Step 3: Results ───────────────────────────────────────────────────────────
def _step_results():
    pid      = st.session_state.get("m3_selected_id")
    analyses = db_load_gainpain(pid)
    if not analyses:
        st.warning("No analysis found.")
        return

    latest = analyses[0]
    result = st.session_state.get("m3_ai_result") or json.loads(latest.get("ai_analysis","{}"))
    band   = latest["priority_band"]
    pb     = PRIORITY_BANDS.get(band, PRIORITY_BANDS["Medium Priority"])
    scaled = latest["priority_score_scaled"]

    st.markdown(f"""
    <div class="step-hdr">
      <h1>Gain–Pain Results</h1>
      <p>{latest['id']} · {latest['analysed_at']} · NIST AI RMF aligned</p>
    </div>""", unsafe_allow_html=True)

    # Priority score card
    st.markdown(f"""
    <div style="background:{pb['bg']};border:1.5px solid {pb['color']};border-radius:14px;
                padding:1.2rem 1.6rem;margin-bottom:1.5rem;
                display:flex;justify-content:space-between;align-items:center;">
      <div>
        <div style="font-size:0.7rem;color:{pb['color']};font-weight:700;letter-spacing:0.08em;">PRIORITY SCORE (NIST)</div>
        <div style="font-size:2rem;font-weight:800;color:{pb['color']};margin-top:2px;">
          {scaled:.1f}<span style="font-size:1rem;opacity:0.6;"> / 10</span>
        </div>
        <div style="font-size:0.78rem;color:{pb['color']};margin-top:2px;">
          Gains avg: {latest['avg_gains']:.2f}/5 · Pains avg: {latest['avg_pains']:.2f}/5
        </div>
      </div>
      <div style="font-size:1rem;font-weight:700;color:{pb['color']};">{pb['icon']} {band}</div>
    </div>""", unsafe_allow_html=True)

    # Net benefit summary
    summary = result.get("net_benefit_summary", "")
    if summary:
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #EAEBF5;border-radius:12px;
                    padding:1rem 1.3rem;margin-bottom:1.4rem;font-size:0.9rem;
                    color:#444;line-height:1.6;">
          {summary}
        </div>""", unsafe_allow_html=True)

    # Gains vs Pains side by side
    col_g, col_p = st.columns(2, gap="medium")
    gain_reasoning = result.get("gain_reasoning", {})
    pain_reasoning = result.get("pain_reasoning", {})
    gains_data     = result.get("gains", {})
    pains_data     = result.get("pains", {})

    with col_g:
        st.markdown("""
        <div style="font-weight:700;font-size:0.9rem;color:#1D9E75;margin-bottom:0.8rem;">
          📈 Gains
        </div>""", unsafe_allow_html=True)
        for d in GAIN_DIMENSIONS:
            s   = gains_data.get(d["id"], 0)
            pct = int(s / 5 * 100)
            col = "#1D9E75"
            rsn = gain_reasoning.get(d["id"], "")
            st.markdown(f"""
            <div style="margin-bottom:0.9rem;">
              <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:3px;">
                <span>{d['icon']} {d['label']} <span style="color:#aaa;font-size:0.7rem;">{d['nist']}</span></span>
                <span style="font-weight:700;color:{col};">{s:.1f}/5</span>
              </div>
              <div style="background:#F0F0F8;border-radius:6px;height:7px;">
                <div style="background:{col};width:{pct}%;height:7px;border-radius:6px;"></div>
              </div>
              <div style="font-size:0.75rem;color:#888;margin-top:3px;">{rsn}</div>
            </div>""", unsafe_allow_html=True)

    with col_p:
        st.markdown("""
        <div style="font-weight:700;font-size:0.9rem;color:#C0392B;margin-bottom:0.8rem;">
          📉 Pains
        </div>""", unsafe_allow_html=True)
        for d in PAIN_DIMENSIONS:
            s   = pains_data.get(d["id"], 0)
            pct = int(s / 5 * 100)
            col = "#C0392B" if s >= 3.5 else "#C07A10" if s >= 2.5 else "#1D9E75"
            rsn = pain_reasoning.get(d["id"], "")
            st.markdown(f"""
            <div style="margin-bottom:0.9rem;">
              <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:3px;">
                <span>{d['icon']} {d['label']} <span style="color:#aaa;font-size:0.7rem;">{d['nist']}</span></span>
                <span style="font-weight:700;color:{col};">{s:.1f}/5</span>
              </div>
              <div style="background:#F0F0F8;border-radius:6px;height:7px;">
                <div style="background:{col};width:{pct}%;height:7px;border-radius:6px;"></div>
              </div>
              <div style="font-size:0.75rem;color:#888;margin-top:3px;">{rsn}</div>
            </div>""", unsafe_allow_html=True)

    # Chart
    chart_data = pd.DataFrame({
        "Dimension": [d["label"] for d in GAIN_DIMENSIONS] + [d["label"] for d in PAIN_DIMENSIONS],
        "Score":     [gains_data.get(d["id"], 0) for d in GAIN_DIMENSIONS] +
                     [pains_data.get(d["id"], 0) for d in PAIN_DIMENSIONS],
        "Type":      ["Gain"] * len(GAIN_DIMENSIONS) + ["Pain"] * len(PAIN_DIMENSIONS),
    })
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.bar_chart(chart_data.set_index("Dimension")["Score"], color="#6C63FF")

    # Quick wins + mitigations
    quick_wins   = result.get("quick_wins", [])
    mitigations  = result.get("mitigation_actions", [])
    next_step    = result.get("recommended_next_step", "")

    qw_col, mt_col = st.columns(2, gap="medium")
    with qw_col:
        if quick_wins:
            st.markdown("**⚡ Quick Wins**")
            for q in quick_wins:
                st.markdown(f"- {q}")
    with mt_col:
        if mitigations:
            st.markdown("**🛡️ Pain Mitigations**")
            for m in mitigations:
                st.markdown(f"- {m}")

    if next_step:
        st.info(f"**Recommended next step:** {next_step}")

    # Export
    export_row = {
        "Analysis ID":    latest["id"],
        "Problem ID":     pid,
        "Analysed at":    latest["analysed_at"],
        "Priority Band":  band,
        "Priority Score": f"{scaled:.1f}/10",
        "Avg Gains":      f"{latest['avg_gains']:.2f}",
        "Avg Pains":      f"{latest['avg_pains']:.2f}",
    }
    for d in GAIN_DIMENSIONS:
        export_row[d["label"]] = gains_data.get(d["id"], 0)
    for d in PAIN_DIMENSIONS:
        export_row[d["label"]] = pains_data.get(d["id"], 0)

    csv = pd.DataFrame([export_row]).to_csv(index=False).encode("utf-8")
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.download_button("⬇️ Download CSV", csv,
                       f"gainpain_{latest['id']}.csv", "text/csv",
                       use_container_width=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("Done →", type="primary", use_container_width=True):
        st.session_state.m3_step = "done"
        st.rerun()


# ── Step 4: Done ──────────────────────────────────────────────────────────────
def _step_done():
    pid      = st.session_state.get("m3_selected_id", "")
    analyses = db_load_gainpain(pid)
    band     = analyses[0]["priority_band"] if analyses else "—"
    scaled   = analyses[0]["priority_score_scaled"] if analyses else 0
    pb       = PRIORITY_BANDS.get(band, PRIORITY_BANDS["Medium Priority"])
    badge_cls = {"High Priority":"b-approved","Medium Priority":"b-review","Low Priority":"b-rejected"}.get(band,"b-submitted")

    st.markdown("""
    <div class="step-hdr">
      <h1>Analysis Complete</h1>
      <p>The gain-pain analysis has been recorded and the problem status updated.</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ref-wrap">
      <div>
        <div class="ref-meta">Problem ID</div>
        <div class="ref-id">{pid}</div>
      </div>
      <div style="text-align:right;">
        <div class="ref-meta">Priority</div>
        <span class="badge {badge_cls}">{band} · {scaled:.1f}/10</span>
      </div>
    </div>""", unsafe_allow_html=True)

    st.info("This use case is now ready for **Module 4 — Governance Dashboard** review.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Analyse another", use_container_width=True):
            st.session_state.m3_step        = "pick"
            st.session_state.m3_selected_id = None
            st.session_state.m3_ai_result   = None
            st.rerun()
    with col2:
        if st.button("Go to Module 4 →", type="primary", use_container_width=True):
            st.session_state.active_module = "m4"
            st.rerun()


# ── AI call ───────────────────────────────────────────────────────────────────
def _call_m3_ai(problem: dict, assessment: dict) -> dict | None:
    prompt = f"""{M3_GAINPAIN_PROMPT}

PROBLEM STATEMENT (Module 1):
- Problem: {problem.get('problem_statement','')}
- Objective: {problem.get('business_objective','')}
- Solution: {problem.get('solution_approach','')}
- Business value: {problem.get('business_value','')}
- Workflow: {problem.get('workflow_location','')}
- Timeline: {problem.get('timeline','')}
- Owner: {problem.get('action_owner','')}
- ISO Risk Category: {problem.get('iso_risk_category','Not specified')}
- Affected stakeholders: {problem.get('affected_stakeholders','')}
- Success criteria: {problem.get('success_criteria','')}

FEASIBILITY ASSESSMENT (Module 2):
- Overall score: {assessment.get('overall_score',0):.2f}/5
- Verdict: {assessment.get('verdict','—')}
- AI Suitability: {assessment.get('ai_suitability_score',0):.1f}
- Economic Viability: {assessment.get('economic_viability_score',0):.1f}
- Data Readiness: {assessment.get('data_readiness_score',0):.1f}
- Workflow Maturity: {assessment.get('workflow_maturity_score',0):.1f}
- Change Management: {assessment.get('change_management_score',0):.1f}
- Risk & Compliance: {assessment.get('risk_compliance_score',0):.1f}
- Hard gate triggered: {bool(assessment.get('hard_gate_triggered',0))}

Apply the NIST priority score formula and return ONLY the JSON object."""

    try:
        raw    = call_ai(prompt)
        text   = clean_llm_json(raw)
        return json.loads(text)
    except json.JSONDecodeError as e:
        st.error(f"AI returned malformed JSON: {e}")
        st.code(raw[:600], language="json")
        return None
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return None
