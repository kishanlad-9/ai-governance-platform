# modules/module1/chat.py
# Module 1 — single page, step-by-step flow
# Step 1: Chat until all 8 fields captured
# Step 2: Summary table review
# Step 3: Submit → reference ID

import streamlit as st
from datetime import datetime

from config.constants import REQUIRED_FIELDS, FIELD_KEYS
from database.db import db_insert_record, db_load_all
from utils.helpers import call_m1_ai, parse_extracted, strip_json, is_field_done


def render():
    step = st.session_state.get("m1_step", "chat")

    if step == "chat":
        _step_chat()
    elif step == "summary":
        _step_summary()
    elif step == "done":
        _step_done()


# ── Step 1: Conversation ──────────────────────────────────────────────────────
def _step_chat():
    st.markdown("""
    <div class="step-hdr">
      <h1>Problem Definition</h1>
      <p>Describe your business problem. Answer each question until all fields are captured.</p>
    </div>""", unsafe_allow_html=True)

    # Chat history
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown("""
        <div class="bubble-ai">
          <div class="bubble-label">AI ANALYST</div>
          Hi! Please describe the business problem you're trying to solve with AI.
        </div>""", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        text = strip_json(msg["content"])
        if not text:
            continue
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display:flex;flex-direction:column;align-items:flex-end;">
              <div class="bubble-label user">YOU</div>
              <div class="bubble-user">{text}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div>
              <div class="bubble-label">AI ANALYST</div>
              <div class="bubble-ai">{text}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Show "Review Summary" button once all fields are ready
    if st.session_state.extracted.get("ready_to_submit"):
        st.success("All fields captured.")
        if st.button("Review Summary →", type="primary", use_container_width=True):
            st.session_state.m1_step = "summary"
            st.rerun()
        return

    # Chat input
    user_input = st.chat_input("Type your answer…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner(""):
            ai_resp = call_m1_ai(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": ai_resp})
        parsed = parse_extracted(ai_resp)
        if parsed:
            for k in FIELD_KEYS:
                v = parsed.get(k)
                if v and v != "null":
                    st.session_state.extracted[k] = v
            st.session_state.extracted["completeness_pct"] = parsed.get("completeness_pct", 0)
            st.session_state.extracted["ready_to_submit"]  = parsed.get("ready_to_submit", False)
        st.rerun()


# ── Step 2: Summary table ─────────────────────────────────────────────────────
def _step_summary():
    st.markdown("""
    <div class="step-hdr">
      <h1>Review Summary</h1>
      <p>Confirm all captured information before submitting.</p>
    </div>""", unsafe_allow_html=True)

    ext = st.session_state.extracted

    rows_html = ""
    for key, label in REQUIRED_FIELDS:
        val = ext.get(key) or "—"
        rows_html += f"""
        <div class="sum-row">
          <div class="sum-key">{label}</div>
          <div class="sum-val">{val}</div>
        </div>"""

    st.markdown(f'<div class="sum-wrap">{rows_html}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Edit", use_container_width=True):
            st.session_state.m1_step = "chat"
            st.rerun()
    with col2:
        if st.button("Submit →", type="primary", use_container_width=True):
            _submit()


# ── Step 3: Confirmation ──────────────────────────────────────────────────────
def _step_done():
    sid = st.session_state.get("submission_id", "")
    st.markdown("""
    <div class="step-hdr">
      <h1>Submitted</h1>
      <p>Your problem statement has been recorded.</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ref-wrap">
      <div>
        <div class="ref-meta">Reference ID</div>
        <div class="ref-id">{sid}</div>
      </div>
      <div style="text-align:right;">
        <div class="ref-meta">Status</div>
        <span class="badge b-submitted">Submitted</span>
      </div>
    </div>""", unsafe_allow_html=True)

    st.info("Proceed to **Feasibility Assessment** to evaluate this use case.")

    if st.button("Go to Feasibility Assessment →", type="primary", use_container_width=True):
        st.session_state.active_module = "m2"
        st.session_state.m2_selected_id = sid.replace("GRP", "GRP") # keep same
        st.session_state.m2_sub = "select"
        st.rerun()


# ── Submit helper ─────────────────────────────────────────────────────────────
def _submit():
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
    st.session_state.m1_step           = "done"
    st.rerun()
