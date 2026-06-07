# modules/module1/log.py
# Module 1 — Submissions Log page
# Search by reference ID, table view, detail view, status update, CSV export

import streamlit as st
import pandas as pd
from datetime import datetime

from config.constants import REQUIRED_FIELDS, FIELD_KEYS, STATUS_OPTIONS, STATUS_BADGE
from database.db import db_search, db_update_status, db_load_all


def render():
    st.markdown("""
    <div class="page-hdr">
      <h2>🗂️ Submissions Log</h2>
      <p>Search, review, and manage all submitted problem statements. Search by reference ID or any keyword.</p>
    </div>""", unsafe_allow_html=True)

    records = st.session_state.submitted_records
    if not records:
        st.markdown("""
        <div class="coming-soon">
          <h3>No submissions yet</h3>
          <p>Complete the AI conversation and submit a problem statement to see it here.</p>
        </div>""", unsafe_allow_html=True)
        return

    # ── Search bar ────────────────────────────────────────────────────────────
    sc1, sc2 = st.columns([5, 1])
    with sc1:
        q = st.text_input(
            "search",
            placeholder="🔍  Search by reference ID (e.g. GRP-20240601-143022) or any keyword…",
            label_visibility="collapsed",
            key="search_query"
        )
    with sc2:
        if st.button("Clear", use_container_width=True):
            st.session_state.search_query = ""
            st.rerun()

    filtered = db_search(q) if q else records
    if q:
        st.caption(f"**{len(filtered)}** result(s) for '{q}'")

    tab_tbl, tab_detail, tab_export = st.tabs([
        f"📊 All Records ({len(filtered)})",
        "🔍 Detail View",
        "⬇️ Export CSV",
    ])

    with tab_tbl:
        _render_table(filtered)

    with tab_detail:
        _render_detail(filtered)

    with tab_export:
        _render_export(filtered)


def _render_table(filtered: list):
    if not filtered:
        st.info("No records match your search.")
        return
    col_map = {
        "id":                "Reference ID",
        "submitted_at":      "Submitted",
        "status":            "Status",
        "problem_statement": "Problem Statement",
        "business_objective":"Objective",
        "solution_approach": "Solution",
        "timeline":          "Timeline",
        "action_owner":      "Owner",
        "workflow_location": "Workflow",
        "decision_support":  "Decision Support",
        "business_value":    "Business Value",
    }
    df      = pd.DataFrame(filtered).rename(columns=col_map)
    ordered = [v for v in col_map.values() if v in df.columns]
    st.dataframe(
        df[ordered], use_container_width=True, hide_index=True,
        column_config={
            "Reference ID":      st.column_config.TextColumn(width="small"),
            "Submitted":         st.column_config.TextColumn(width="small"),
            "Status":            st.column_config.TextColumn(width="small"),
            "Problem Statement": st.column_config.TextColumn(width="large"),
            "Business Value":    st.column_config.TextColumn(width="medium"),
        }
    )


def _render_detail(filtered: list):
    if not filtered:
        st.info("No records to display.")
        return

    opts   = {r["id"]: f"{r['id']}  —  {r.get('problem_statement','')[:55]}…" for r in filtered}
    sel_id = st.selectbox("Select record", list(opts.keys()),
                          format_func=lambda x: opts[x], key="detail_sel")
    record = next(r for r in filtered if r["id"] == sel_id)
    sc     = STATUS_BADGE.get(record.get("status", "Submitted"), "b-submitted")

    st.markdown(f"""
    <div class="ref-box">
      <div>
        <div class="ref-lbl">Reference ID</div>
        <div class="ref-id">{record['id']}</div>
      </div>
      <div style="text-align:right;">
        <div class="ref-lbl">Submitted</div>
        <div style="color:#888;font-size:0.82rem;">{record.get('submitted_at','—')}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    rows_html = "".join(f"""
    <tr><td class="lbl-col">{label}</td><td>{record.get(key,'—') or '—'}</td></tr>"""
        for key, label in REQUIRED_FIELDS)

    st.markdown(f"""
    <div class="scard">
      <div style="margin-bottom:0.8rem;"><span class="badge {sc}">{record.get('status','')}</span></div>
      <table class="sum-table">
        <thead><tr><th>Field</th><th>Value</th></tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>""", unsafe_allow_html=True)

    # Status update
    st.markdown("**Update status**")
    u1, u2 = st.columns([3, 1])
    with u1:
        cur   = record.get("status", "Submitted")
        new_s = st.selectbox(
            "Status", STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(cur) if cur in STATUS_OPTIONS else 0,
            label_visibility="collapsed", key=f"ssel_{record['id']}"
        )
    with u2:
        if st.button("Update", use_container_width=True, key=f"sbtn_{record['id']}"):
            db_update_status(record["id"], new_s)
            st.session_state.submitted_records = db_load_all()
            st.success(f"Updated to **{new_s}**")
            st.rerun()


def _render_export(filtered: list):
    df_exp = pd.DataFrame(filtered)
    csv    = df_exp.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download as CSV", csv,
        f"ai_governance_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv", use_container_width=True
    )
    st.dataframe(df_exp, use_container_width=True, hide_index=True)
    st.caption(f"{len(filtered)} records · {len(FIELD_KEYS)+3} fields each")
