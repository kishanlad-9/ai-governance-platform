# modules/module1/extract.py
# Module 1 — Extracted Information page
# Shows all 8 field cards + final summary table + submit button when complete

import streamlit as st
from datetime import datetime

from config.constants import REQUIRED_FIELDS, FIELD_KEYS
from database.db import db_insert_record, db_load_all
from utils.helpers import is_field_done, get_completeness_color


def render():
    st.markdown("""
    <div class="page-hdr">
      <h2>📊 Extracted Information</h2>
      <p>Live view of all 8 fields captured from your conversation. Updates automatically.</p>
    </div>""", unsafe_allow_html=True)

    ext      = st.session_state.extracted
    captured = sum(1 for k in FIELD_KEYS if is_field_done(k))
    pct      = ext.get("completeness_pct", 0)

    # ── Metrics row ───────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("Fields Captured", f"{captured} / 8")
    c2.metric("Completeness",    f"{pct}%")
    c3.metric("Status",          st.session_state.current_status.title())

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # ── Field cards grid ──────────────────────────────────────────────────────
    col_a, col_b = st.columns(2, gap="medium")
    for i, (key, label) in enumerate(REQUIRED_FIELDS):
        val    = ext.get(key)
        filled = is_field_done(key)
        done   = "done" if filled else ""
        target = col_a if i % 2 == 0 else col_b
        with target:
            st.markdown(f"""
            <div class="fcard {done}" style="min-height:70px;">
              <div class="fcard-lbl {done}">{label}</div>
              <div class="fcard-val {'pending' if not filled else ''}">{val if filled else 'Not yet captured — continue the conversation'}</div>
            </div>""", unsafe_allow_html=True)

    # ── Summary table + submit (when all 8 are done) ──────────────────────────
    if captured == 8:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### ✅ Complete Problem Statement Summary")
        st.caption("All fields captured. Review below before submitting.")

        rows_html = "".join(f"""
        <tr>
          <td class="lbl-col">{label}</td>
          <td>{ext.get(key, '—') or '—'}</td>
        </tr>""" for key, label in REQUIRED_FIELDS)

        st.markdown(f"""
        <div class="scard">
          <table class="sum-table">
            <thead><tr><th>Field</th><th>Captured Value</th></tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>""", unsafe_allow_html=True)

        _render_submit()
        _render_confirmation()


def _render_submit():
    if not st.session_state.extracted.get("ready_to_submit"):
        return
    if st.session_state.current_status == "submitted":
        return
    st.session_state.current_status = "complete"
    st.success("✅ All 8 fields captured. Submit when ready.")
    if st.button("🚀  Submit to Governance Committee", type="primary",
                 use_container_width=True, key="extract_submit"):
        record = {
            "id":           f"GRP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status":       "Submitted",
            **{k: st.session_state.extracted.get(k, "") for k in FIELD_KEYS},
        }
        db_insert_record(record)
        st.session_state.submitted_records = db_load_all()
        st.session_state.submission_id     = record["id"]
        st.session_state.current_status    = "submitted"
        st.rerun()


def _render_confirmation():
    if st.session_state.current_status != "submitted":
        return
    sid = st.session_state.submission_id
    st.balloons()
    st.markdown(f"""
    <div class="ref-box">
      <div>
        <div class="ref-lbl">Successfully submitted</div>
        <div class="ref-id">{sid}</div>
      </div>
      <div style="text-align:right;font-size:0.8rem;color:#7effc8;">Queued for Module 2 →</div>
    </div>""", unsafe_allow_html=True)
    st.info("Problem statement queued for **Module 2 — Feasibility & Readiness Assessment**.")
