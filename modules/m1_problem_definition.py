# modules/m1_problem_definition.py
# ─────────────────────────────────────────────────────────────────────────────
# Module 1 — Problem Definition
# Pages: AI Conversation · Extracted Info · Progress Tracking · Submissions Log
#
# Entry point: render(sub)  — called from app.py based on active_sub.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
from datetime import datetime

from config.constants import REQUIRED_FIELDS, FIELD_KEYS, STATUS_OPTIONS, STATUS_BADGE
from core.database    import db_insert_record, db_load_all, db_update_status, db_search
from core.ai_client   import call_m1_ai
from utils.helpers    import (get_completeness_color, parse_extracted,
                               strip_json, is_field_done)


# ── Public router ─────────────────────────────────────────────────────────────

def render(sub: str):
    """Route to the correct M1 sub-page."""
    if   sub == "chat":    _page_chat()
    elif sub == "extract": _page_extract()
    elif sub == "track":   _page_track()
    elif sub == "log":     _page_log()


# ── Page: AI Conversation ─────────────────────────────────────────────────────

def _page_chat():
    st.markdown("""
    <div class="page-hdr">
      <h2>💬 AI Conversation</h2>
      <p>Describe your business problem. The AI analyst will ask follow-up questions to capture all 8 required fields.</p>
    </div>""", unsafe_allow_html=True)

    chat_col, info_col = st.columns([1.15, 0.85], gap="large")

    with chat_col:
        st.markdown('<div class="scard">', unsafe_allow_html=True)

        # Welcome message on first load
        if not st.session_state.messages:
            st.markdown("""
            <div class="chat-a">
              <div class="chat-lbl">AI GOVERNANCE ANALYST</div>
              Welcome! I'm here to help you structure your AI use case for governance review.<br><br>
              Please start by describing the business problem you're trying to solve — in your own words.
              I'll guide you through capturing all the required information.
            </div>""", unsafe_allow_html=True)

        for msg in st.session_state.messages:
            content = strip_json(msg["content"])
            if not content:
                continue
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-u"><div class="chat-lbl">YOU</div>{content}</div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="chat-a"><div class="chat-lbl">AI GOVERNANCE ANALYST</div>{content}</div>',
                    unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        _render_submit()
        _render_confirmation()

        if st.session_state.current_status != "submitted":
            user_input = st.chat_input("Describe your problem or answer the question above…")
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.spinner("Analysing…"):
                    ai_resp = call_m1_ai(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_resp})

                parsed = parse_extracted(ai_resp)
                if parsed:
                    for k in FIELD_KEYS:
                        v = parsed.get(k)
                        if v and v != "null":
                            st.session_state.extracted[k] = v
                    st.session_state.extracted["completeness_pct"] = parsed.get("completeness_pct", 0)
                    st.session_state.extracted["ready_to_submit"]   = parsed.get("ready_to_submit", False)
                st.rerun()

    with info_col:
        _render_live_extraction_panel()


# ── Page: Extracted Info ──────────────────────────────────────────────────────

def _page_extract():
    st.markdown("""
    <div class="page-hdr">
      <h2>📊 Extracted Information</h2>
      <p>Live view of all 8 fields captured from your conversation. Updates automatically.</p>
    </div>""", unsafe_allow_html=True)

    ext      = st.session_state.extracted
    captured = sum(1 for k in FIELD_KEYS if is_field_done(k))
    pct      = ext.get("completeness_pct", 0)
    color    = get_completeness_color(pct)

    c1, c2, c3 = st.columns(3)
    c1.metric("Fields Captured", f"{captured} / 8")
    c2.metric("Completeness",    f"{pct}%")
    c3.metric("Status",          st.session_state.current_status.title())

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

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

    if captured == 8:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### ✅ Complete Problem Statement Summary")
        st.caption("All fields captured. Review below before submitting.")
        rows_html = "".join(f"""
        <tr>
          <td class="lbl-col">{label}</td>
          <td>{ext.get(key,'—') or '—'}</td>
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


# ── Page: Progress Tracking ───────────────────────────────────────────────────

def _page_track():
    st.markdown("""
    <div class="page-hdr">
      <h2>📈 Progress Tracking</h2>
      <p>Monitor completion status of the current problem statement and all past submissions.</p>
    </div>""", unsafe_allow_html=True)

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
    </div>""", unsafe_allow_html=True)

    rows = []
    for key, label in REQUIRED_FIELDS:
        done = is_field_done(key)
        preview = (st.session_state.extracted.get(key) or "")[:60] + "…" if done else "—"
        rows.append({"Field": label, "Status": "✅ Captured" if done else "⏳ Pending",
                     "Value preview": preview})
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True,
        column_config={
            "Field":         st.column_config.TextColumn(width="medium"),
            "Status":        st.column_config.TextColumn(width="small"),
            "Value preview": st.column_config.TextColumn(width="large"),
        })
    st.markdown("</div>", unsafe_allow_html=True)

    records = st.session_state.submitted_records
    if records:
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


# ── Page: Submissions Log ─────────────────────────────────────────────────────

def _page_log():
    st.markdown("""
    <div class="page-hdr">
      <h2>🗂️ Submissions Log</h2>
      <p>Search, review, and manage all submitted problem statements.</p>
    </div>""", unsafe_allow_html=True)

    records = st.session_state.submitted_records
    if not records:
        st.markdown("""
        <div class="coming-soon">
          <h3>No submissions yet</h3>
          <p>Complete the AI conversation and submit a problem statement to see it here.</p>
        </div>""", unsafe_allow_html=True)
        return

    sc1, sc2 = st.columns([5, 1])
    with sc1:
        q = st.text_input("search", placeholder="🔍  Search by reference ID or any keyword…",
                          label_visibility="collapsed", key="search_query")
    with sc2:
        if st.button("Clear", use_container_width=True):
            st.session_state.search_query = ""
            st.rerun()

    filtered = db_search(q) if q else records
    if q:
        st.caption(f"**{len(filtered)}** result(s) for '{q}'")

    tab_tbl, tab_detail, tab_export = st.tabs([
        f"📊 All Records ({len(filtered)})", "🔍 Detail View", "⬇️ Export CSV"
    ])

    with tab_tbl:
        if filtered:
            col_map = {
                "id": "Reference ID", "submitted_at": "Submitted", "status": "Status",
                "problem_statement": "Problem Statement", "business_objective": "Objective",
                "solution_approach": "Solution", "timeline": "Timeline",
                "action_owner": "Owner", "workflow_location": "Workflow",
                "decision_support": "Decision Support", "business_value": "Business Value",
            }
            df = pd.DataFrame(filtered).rename(columns=col_map)
            ordered = [v for v in col_map.values() if v in df.columns]
            st.dataframe(df[ordered], use_container_width=True, hide_index=True,
                column_config={
                    "Reference ID":      st.column_config.TextColumn(width="small"),
                    "Submitted":         st.column_config.TextColumn(width="small"),
                    "Status":            st.column_config.TextColumn(width="small"),
                    "Problem Statement": st.column_config.TextColumn(width="large"),
                    "Business Value":    st.column_config.TextColumn(width="medium"),
                })
        else:
            st.info("No records match your search.")

    with tab_detail:
        if not filtered:
            st.info("No records to display.")
        else:
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

            st.markdown('<div class="scard">', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-bottom:0.8rem;"><span class="badge {sc}">{record.get("status","")}</span></div>',
                        unsafe_allow_html=True)
            rows_html = "".join(f"""
            <tr><td class="lbl-col">{label}</td><td>{record.get(key,'—') or '—'}</td></tr>"""
                for key, label in REQUIRED_FIELDS)
            st.markdown(f"""
            <table class="sum-table">
              <thead><tr><th>Field</th><th>Value</th></tr></thead>
              <tbody>{rows_html}</tbody>
            </table>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("**Update status**")
            u1, u2 = st.columns([3, 1])
            with u1:
                cur   = record.get("status", "Submitted")
                new_s = st.selectbox("Status", STATUS_OPTIONS,
                                     index=STATUS_OPTIONS.index(cur) if cur in STATUS_OPTIONS else 0,
                                     label_visibility="collapsed", key=f"ssel_{record['id']}")
            with u2:
                if st.button("Update", use_container_width=True, key=f"sbtn_{record['id']}"):
                    db_update_status(record["id"], new_s)
                    st.session_state.submitted_records = db_load_all()
                    st.success(f"Updated to **{new_s}**")
                    st.rerun()

    with tab_export:
        df_exp = pd.DataFrame(filtered)
        csv    = df_exp.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download as CSV", csv,
                           f"ai_governance_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                           "text/csv", use_container_width=True)
        st.dataframe(df_exp, use_container_width=True, hide_index=True)
        st.caption(f"{len(filtered)} records · {len(FIELD_KEYS)+3} fields each")


# ── Shared sub-page helpers ───────────────────────────────────────────────────

def _render_live_extraction_panel():
    ext      = st.session_state.extracted
    captured = sum(1 for k in FIELD_KEYS if is_field_done(k))
    pct      = ext.get("completeness_pct", 0)
    color    = get_completeness_color(pct)

    st.markdown(f"""
    <div class="scard">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
        <span style="font-weight:700;font-size:0.95rem;color:#1a1a2e;">📊 Extracted Info</span>
        <span style="font-size:0.8rem;font-weight:700;color:{color};">{captured}/8</span>
      </div>
      <div style="background:#f0f0f8;border-radius:8px;height:5px;margin-bottom:1rem;">
        <div style="background:{color};width:{pct}%;height:5px;border-radius:8px;transition:width 0.4s;"></div>
      </div>
    """, unsafe_allow_html=True)

    for key, label in REQUIRED_FIELDS:
        val    = ext.get(key)
        filled = is_field_done(key)
        done   = "done" if filled else ""
        st.markdown(f"""
        <div class="fcard {done}">
          <div class="fcard-lbl {done}">{label}</div>
          <div class="fcard-val {'pending' if not filled else ''}">{val if filled else 'Waiting…'}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_submit():
    if not st.session_state.extracted.get("ready_to_submit"):
        return
    if st.session_state.current_status == "submitted":
        return

    st.session_state.current_status = "complete"
    st.success("✅ All 8 fields captured. Review the summary and submit when ready.")

    if st.button("🚀  Submit to Governance Committee", type="primary", use_container_width=True):
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
    st.info("This problem statement is now queued for **Module 2 — Feasibility & Readiness Assessment**.")
