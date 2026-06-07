# modules/module1/tracking.py
# Module 1 — Progress Tracking page
# Shows field-level status + submission history metrics + status chart

import streamlit as st
import pandas as pd

from config.constants import REQUIRED_FIELDS, FIELD_KEYS
from utils.helpers import is_field_done, get_completeness_color


def render():
    st.markdown("""
    <div class="page-hdr">
      <h2>📈 Progress Tracking</h2>
      <p>Monitor completion status of the current problem statement and all past submissions.</p>
    </div>""", unsafe_allow_html=True)

    _render_current_progress()
    _render_submission_history()


def _render_current_progress():
    pct      = st.session_state.extracted.get("completeness_pct", 0)
    color    = get_completeness_color(pct)
    captured = sum(1 for k in FIELD_KEYS if is_field_done(k))

    st.markdown('<div class="scard">', unsafe_allow_html=True)
    st.markdown("#### Current Problem Statement")
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:6px;">
      <span>Overall completion</span>
      <span style="color:{color};font-weight:700;">{pct}%  ({captured}/8 fields)</span>
    </div>
    <div style="background:#f0f0f8;border-radius:10px;height:12px;margin-bottom:1.2rem;">
      <div style="background:{color};width:{pct}%;height:12px;border-radius:10px;transition:width 0.4s;"></div>
    </div>
    """, unsafe_allow_html=True)

    rows = []
    for key, label in REQUIRED_FIELDS:
        done  = is_field_done(key)
        val   = st.session_state.extracted.get(key) or ""
        rows.append({
            "Field":         label,
            "Status":        "✅ Captured" if done else "⏳ Pending",
            "Value preview": (val[:60] + "…") if done else "—",
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Field":         st.column_config.TextColumn(width="medium"),
            "Status":        st.column_config.TextColumn(width="small"),
            "Value preview": st.column_config.TextColumn(width="large"),
        }
    )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_submission_history():
    records = st.session_state.submitted_records
    if not records:
        return

    st.markdown('<div class="scard" style="margin-top:1rem;">', unsafe_allow_html=True)
    st.markdown("#### Submission History")

    total     = len(records)
    approved  = sum(1 for r in records if r.get("status") == "Approved")
    submitted = sum(1 for r in records if r.get("status") == "Submitted")
    under_rev = sum(1 for r in records if r.get("status") == "Under Review")
    rejected  = sum(1 for r in records if r.get("status") == "Rejected")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total",        total)
    m2.metric("Submitted",    submitted)
    m3.metric("Under Review", under_rev)
    m4.metric("Approved",     approved)
    m5.metric("Rejected",     rejected)

    status_counts = {}
    for r in records:
        s = r.get("status", "Unknown")
        status_counts[s] = status_counts.get(s, 0) + 1
    df_chart = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
    st.bar_chart(df_chart.set_index("Status"))
    st.markdown("</div>", unsafe_allow_html=True)
