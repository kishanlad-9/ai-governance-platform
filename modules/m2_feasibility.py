# modules/m2_feasibility.py
# ─────────────────────────────────────────────────────────────────────────────
# Module 2 — AI Feasibility & Readiness Assessment
# Pages: Select Problem · AI Assessment · Results · All Assessments
#
# The assessment is fully AI-driven: the system reads the M1 problem statement
# and automatically scores all 25 criteria across 5 stakeholder dimensions.
#
# Entry point: render(sub)  — called from app.py based on m2_sub.
# ─────────────────────────────────────────────────────────────────────────────

import json
import streamlit as st
import pandas as pd
from datetime import datetime

from config.constants  import REQUIRED_FIELDS, STATUS_BADGE, VERDICT_CONFIG
from config.dimensions import ASSESSMENT_DIMENSIONS
from core.database     import (db_load_assessments, db_save_assessment,
                                db_update_status, db_load_all)
from core.ai_client    import call_m2_scoring, call_m2_report
from utils.helpers     import get_completeness_color, score_to_verdict


# ── Public router ─────────────────────────────────────────────────────────────

def render(sub: str):
    """Route to the correct M2 sub-page."""
    if   sub == "select":     _page_select()
    elif sub == "assess":     _page_assess()
    elif sub == "results":    _page_results()
    elif sub == "all_assess": _page_all()


# ── Page: Select Problem ──────────────────────────────────────────────────────

def _page_select():
    st.markdown("""
    <div class="page-hdr">
      <h2>🎯 Select Problem to Assess</h2>
      <p>Choose a submitted problem statement from Module 1 to run the AI feasibility assessment on.</p>
    </div>""", unsafe_allow_html=True)

    records = st.session_state.submitted_records
    if not records:
        st.markdown("""
        <div class="coming-soon">
          <div style="font-size:2.5rem;margin-bottom:1rem;">📭</div>
          <h3>No submitted problems found</h3>
          <p>Go to Module 1 and submit a problem statement first.</p>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown('<div class="scard">', unsafe_allow_html=True)
    st.markdown("#### Available Problem Statements")
    st.caption("Select a problem to begin the AI feasibility assessment.")

    for r in records:
        sc  = STATUS_BADGE.get(r.get("status", "Submitted"), "b-submitted")
        sel = st.session_state.m2_selected_id == r["id"]
        bdr = "border:2px solid #6C63FF;" if sel else "border:1px solid #E4E5F0;"
        bg  = "background:#F0EEFF;" if sel else "background:#fff;"

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div style="{bdr}{bg}border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:0.5rem;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                <span style="font-family:monospace;font-size:0.8rem;color:#6C63FF;font-weight:700;">{r['id']}</span>
                <span class="badge {sc}">{r.get('status','')}</span>
              </div>
              <div style="font-size:0.9rem;color:#1a1a2e;font-weight:500;margin-bottom:0.25rem;">
                {r.get('problem_statement','')[:100]}…
              </div>
              <div style="font-size:0.75rem;color:#888;">
                Owner: {r.get('action_owner','—')} · Submitted: {r.get('submitted_at','—')}
              </div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
            label = "✓ Selected" if sel else "Select"
            if st.button(label, key=f"m2sel_{r['id']}", use_container_width=True,
                         type="primary" if sel else "secondary"):
                st.session_state.m2_selected_id = r["id"]
                st.session_state.m2_responses   = {}
                st.session_state.m2_scores      = {}
                st.session_state.m2_submitted   = False
                st.session_state.m2_ai_reco     = ""
                # Clear any cached AI scores for this problem
                _clear_score_cache(r["id"])
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.m2_selected_id:
        st.success(f"✅ Problem **{st.session_state.m2_selected_id}** selected. Go to **AI Assessment** in the sidebar.")
        if st.button("→ Proceed to Assessment", type="primary", use_container_width=True):
            st.session_state.m2_sub = "assess"
            st.rerun()


# ── Page: AI Assessment ───────────────────────────────────────────────────────

def _page_assess():
    st.markdown("""
    <div class="page-hdr">
      <h2>🤖 AI Feasibility Assessment</h2>
      <p>The system automatically evaluates AI readiness across 5 dimensions using the problem statement. Review the scores and confirm to generate the report.</p>
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

    # Problem context
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

    scores_key = _scores_cache_key(st.session_state.m2_selected_id)

    # ── First visit: show "Run Assessment" button ─────────────────────────────
    if scores_key not in st.session_state:
        st.markdown("""
        <div class="scard" style="text-align:center;padding:2.5rem;">
          <div style="font-size:2.5rem;margin-bottom:0.8rem;">🤖</div>
          <div style="font-weight:700;font-size:1.05rem;color:#1a1a2e;margin-bottom:0.4rem;">
            AI-Powered Assessment Ready
          </div>
          <div style="font-size:0.85rem;color:#888;margin-bottom:1.4rem;">
            The system will analyse the problem statement and automatically score all
            25 assessment criteria across 5 stakeholder dimensions.
          </div>
        </div>""", unsafe_allow_html=True)

        col_l, col_mid, col_r = st.columns([1, 2, 1])
        with col_mid:
            if st.button("🚀  Run AI Assessment", type="primary", use_container_width=True):
                with st.spinner("AI is analysing the problem statement across all 5 dimensions…"):
                    raw = call_m2_scoring(problem)

                if not raw:
                    st.error("Failed to generate AI scores. Check your API key and try again.")
                    return

                # Validate & clamp every score to 1–5
                validated = {}
                for dim in ASSESSMENT_DIMENSIONS:
                    did = dim["id"]
                    validated[did] = {}
                    for q_id, _ in dim["questions"]:
                        val = raw.get(did, {}).get(q_id, 3)
                        validated[did][q_id] = max(1, min(5, int(val)))

                st.session_state[scores_key] = validated
                st.rerun()
        return

    # ── Scores ready: display them ────────────────────────────────────────────
    responses  = st.session_state[scores_key]
    dim_scores = {}

    st.markdown("""
    <div class="scard" style="border-left:4px solid #6C63FF;background:#F0EEFF;padding:0.9rem 1.2rem;margin-bottom:1rem;">
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="font-size:1.3rem;">🤖</span>
        <div>
          <div style="font-weight:700;color:#4A42CC;font-size:0.92rem;">Assessment completed by AI system</div>
          <div style="font-size:0.78rem;color:#6C63FF;margin-top:2px;">
            Scores were automatically generated by analysing the problem statement
            across all 5 dimensions and 25 criteria.
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    score_labels = {1:"Strongly disagree", 2:"Disagree", 3:"Neutral",
                    4:"Agree", 5:"Strongly agree"}
    score_colors = {1:"#C0392B", 2:"#E24B4A", 3:"#EF9F27", 4:"#5aab8f", 5:"#1D9E75"}

    for dim in ASSESSMENT_DIMENSIONS:
        did      = dim["id"]
        dim_resp = responses.get(did, {})
        q_scores = []

        st.markdown(f"""
        <div class="scard" style="border-left:4px solid {dim['color']};">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.3rem;">
            <span style="font-size:1.4rem;">{dim['icon']}</span>
            <div>
              <div style="font-weight:700;font-size:1rem;color:#1a1a2e;">{dim['label']}</div>
              <div style="font-size:0.75rem;color:#888;">
                Stakeholder: <strong>{dim['role']}</strong> &nbsp;·&nbsp;
                <span style="color:#6C63FF;font-weight:600;">Scored by AI</span>
              </div>
            </div>
          </div>
          <div style="font-size:0.82rem;color:#666;margin-bottom:1rem;">{dim['desc']}</div>
        </div>""", unsafe_allow_html=True)

        for q_id, q_label in dim["questions"]:
            val   = dim_resp.get(q_id, 3)
            q_scores.append(val)
            s_lbl = score_labels.get(val, "")
            s_col = score_colors.get(val, "#aaa")
            pct_q = int(val / 5 * 100)
            st.markdown(f"""
            <div style="margin-bottom:0.65rem;padding:0.5rem 0.8rem;
                        background:#fafafa;border-radius:8px;border:1px solid #f0f0f8;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <span style="font-size:0.82rem;color:#444;">{q_label}</span>
                <span style="font-weight:700;color:{s_col};font-size:0.85rem;
                             white-space:nowrap;margin-left:1rem;">
                  {val}/5 — {s_lbl}
                </span>
              </div>
              <div style="background:#eee;border-radius:4px;height:5px;">
                <div style="background:{s_col};width:{pct_q}%;height:5px;border-radius:4px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

        dim_avg = sum(q_scores) / len(q_scores)
        dim_scores[did] = round(dim_avg, 2)
        col = get_completeness_color(dim_avg / 5 * 100)
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    background:#f8f8fd;border-radius:8px;padding:0.5rem 0.9rem;margin:0.3rem 0 0.8rem;">
          <span style="font-size:0.8rem;color:#666;">Dimension average</span>
          <span style="font-weight:700;color:{col};font-size:1rem;">{dim_avg:.1f} / 5</span>
        </div>
        <hr style="border-color:#f0f0f8;margin:0.5rem 0 1rem;">""", unsafe_allow_html=True)

    # Overall verdict preview
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
                     border-radius:20px;font-weight:700;font-size:1rem;">
          {vc['icon']} {verdict}
        </span>
      </div>
      <div style="background:#eee;border-radius:8px;height:10px;">
        <div style="background:{vc['color']};width:{pct}%;height:10px;border-radius:8px;"></div>
      </div>
      <div style="font-size:0.75rem;color:#aaa;margin-top:6px;">
        ≥3.5 = Feasible · 2.5–3.4 = Conditional · &lt;2.5 = Not Feasible
      </div>
    </div>""", unsafe_allow_html=True)

    # Dimension summary bars
    st.markdown('<div class="scard">', unsafe_allow_html=True)
    st.markdown("**Score breakdown by dimension**")
    for dim in ASSESSMENT_DIMENSIONS:
        s     = dim_scores.get(dim["id"], 0)
        pct_d = int(s / 5 * 100)
        col   = get_completeness_color(pct_d)
        st.markdown(f"""
        <div style="margin-bottom:0.7rem;">
          <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:3px;">
            <span>{dim['icon']} {dim['label']}
              <span style="color:#aaa;font-size:0.7rem;">({dim['role']})</span>
            </span>
            <span style="font-weight:700;color:{col};">{s:.1f}/5</span>
          </div>
          <div style="background:#f0f0f8;border-radius:6px;height:7px;">
            <div style="background:{col};width:{pct_d}%;height:7px;border-radius:6px;"></div>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Action buttons
    col_re, col_sub = st.columns([1, 2])
    with col_re:
        if st.button("🔄  Re-run Assessment", use_container_width=True):
            _clear_score_cache(st.session_state.m2_selected_id)
            st.rerun()
    with col_sub:
        if st.button("✅  Confirm & Generate AI Report", type="primary", use_container_width=True):
            with st.spinner("Generating full AI recommendation report…"):
                ai_reco = call_m2_report(problem, dim_scores, responses)

            rec_id = f"FA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            db_save_assessment({
                "id":                        rec_id,
                "problem_id":                st.session_state.m2_selected_id,
                "assessed_at":               datetime.now().strftime("%Y-%m-%d %H:%M"),
                "assessor_name":             "AI System",
                "ai_suitability_score":      dim_scores.get("ai_suitability", 0),
                "economic_viability_score":  dim_scores.get("economic_viability", 0),
                "data_readiness_score":      dim_scores.get("data_readiness", 0),
                "workflow_maturity_score":   dim_scores.get("workflow_maturity", 0),
                "change_management_score":   dim_scores.get("change_management", 0),
                "overall_score":             overall,
                "verdict":                   verdict,
                "ai_recommendation":         ai_reco,
                "responses":                 json.dumps(responses),
            })
            db_update_status(
                st.session_state.m2_selected_id,
                "Under Review" if verdict == "Feasible" else
                "Deferred"     if verdict == "Conditional" else "Rejected"
            )
            st.session_state.submitted_records = db_load_all()
            st.session_state.m2_scores         = dim_scores
            st.session_state.m2_submitted      = True
            st.session_state.m2_ai_reco        = ai_reco
            st.session_state.m2_sub            = "results"
            st.rerun()


# ── Page: Results ─────────────────────────────────────────────────────────────

def _page_results():
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
        st.info("No assessment found for this problem. Go to **AI Assessment**.")
        return

    latest  = assessments[0]
    verdict = latest["verdict"]
    vc      = VERDICT_CONFIG.get(verdict, VERDICT_CONFIG["Conditional"])
    overall = latest["overall_score"]
    pct     = int(overall / 5 * 100)
    problem = next((r for r in st.session_state.submitted_records if r["id"] == pid), {})

    # Header verdict card
    st.markdown(f"""
    <div class="scard" style="border:2px solid {vc['color']};">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
        <div>
          <div style="font-size:0.72rem;color:#aaa;font-weight:700;letter-spacing:0.08em;">ASSESSMENT REFERENCE</div>
          <div style="font-family:monospace;font-size:1rem;color:#6C63FF;font-weight:700;margin:2px 0;">{latest['id']}</div>
          <div style="font-size:0.75rem;color:#888;">
            Problem: {pid} · Assessed: {latest['assessed_at']} · By: {latest['assessor_name']} 🤖
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:2.2rem;font-weight:800;color:{vc['color']};">
            {overall:.2f}<span style="font-size:1rem;color:#ccc;">/5</span>
          </div>
          <span style="background:{vc['bg']};color:{vc['color']};padding:5px 14px;
                       border-radius:20px;font-weight:700;">{vc['icon']} {verdict}</span>
        </div>
      </div>
      <div style="background:#f0f0f8;border-radius:8px;height:10px;margin-top:1rem;">
        <div style="background:{vc['color']};width:{pct}%;height:10px;border-radius:8px;"></div>
      </div>
    </div>""", unsafe_allow_html=True)

    col_sc, col_prob = st.columns([1.1, 0.9], gap="large")

    with col_sc:
        st.markdown('<div class="scard">', unsafe_allow_html=True)
        st.markdown("**Dimension Scores**")
        dim_score_map = {
            "ai_suitability":     latest["ai_suitability_score"],
            "economic_viability": latest["economic_viability_score"],
            "data_readiness":     latest["data_readiness_score"],
            "workflow_maturity":  latest["workflow_maturity_score"],
            "change_management":  latest["change_management_score"],
        }
        for dim in ASSESSMENT_DIMENSIONS:
            s     = dim_score_map.get(dim["id"], 0)
            pct_d = int(s / 5 * 100)
            col   = get_completeness_color(pct_d)
            st.markdown(f"""
            <div style="margin-bottom:0.85rem;">
              <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:4px;">
                <span>{dim['icon']} <strong>{dim['label']}</strong>
                  <span style="color:#aaa;font-size:0.72rem;">({dim['role']})</span>
                </span>
                <span style="font-weight:700;color:{col};">{s:.1f}/5</span>
              </div>
              <div style="background:#f0f0f8;border-radius:6px;height:8px;">
                <div style="background:{col};width:{pct_d}%;height:8px;border-radius:6px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        df_scores = pd.DataFrame({
            "Dimension": [d["label"] for d in ASSESSMENT_DIMENSIONS],
            "Score":     [dim_score_map.get(d["id"], 0) for d in ASSESSMENT_DIMENSIONS],
        })
        st.markdown('<div class="scard">', unsafe_allow_html=True)
        st.markdown("**Score chart**")
        st.bar_chart(df_scores.set_index("Dimension"), color="#6C63FF")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_prob:
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

    # AI Recommendation Report
    ai_reco = latest.get("ai_recommendation", "")
    if ai_reco:
        st.markdown('<div class="scard" style="border-left:4px solid #6C63FF;">', unsafe_allow_html=True)
        st.markdown("### 🤖 AI Recommendation Report")
        st.markdown(ai_reco)
        st.markdown("</div>", unsafe_allow_html=True)

    # Export
    df_exp = pd.DataFrame([{
        "Assessment ID":    latest["id"],
        "Problem ID":       pid,
        "Assessed at":      latest["assessed_at"],
        "Assessor":         latest["assessor_name"],
        "AI Suitability":   latest["ai_suitability_score"],
        "Economic Viability": latest["economic_viability_score"],
        "Data Readiness":   latest["data_readiness_score"],
        "Workflow Maturity": latest["workflow_maturity_score"],
        "Change Management": latest["change_management_score"],
        "Overall Score":    latest["overall_score"],
        "Verdict":          latest["verdict"],
    }])
    csv = df_exp.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Results CSV", csv,
                       f"feasibility_{latest['id']}.csv", "text/csv",
                       use_container_width=True)


# ── Page: All Assessments ─────────────────────────────────────────────────────

def _page_all():
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

    total     = len(assessments)
    feasible  = sum(1 for a in assessments if a["verdict"] == "Feasible")
    cond      = sum(1 for a in assessments if a["verdict"] == "Conditional")
    not_f     = sum(1 for a in assessments if a["verdict"] == "Not Feasible")
    avg_score = sum(a["overall_score"] for a in assessments) / total

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Assessments", total)
    m2.metric("✅ Feasible",       feasible)
    m3.metric("⚠️ Conditional",   cond)
    m4.metric("❌ Not Feasible",   not_f)
    m5.metric("Avg Score",         f"{avg_score:.2f}/5")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

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

    csv = pd.DataFrame(assessments).to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Export All Assessments CSV", csv,
        f"all_assessments_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv", use_container_width=True,
    )


# ── Private helpers ───────────────────────────────────────────────────────────

def _scores_cache_key(problem_id: str) -> str:
    return f"m2_ai_scores_{problem_id}"


def _clear_score_cache(problem_id: str):
    key = _scores_cache_key(problem_id)
    if key in st.session_state:
        del st.session_state[key]
