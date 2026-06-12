# ui/sidebar.py
# ─────────────────────────────────────────────────────────────────────────────
# Sidebar: logo, API key input, module navigation, sub-navigation,
# status badge, and "New Problem Statement" reset button.
#
# To add a new module to the nav, add an entry to MODULES below and wire
# its sub-pages in the sub-nav section.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
from core.database import db_load_all

# Module registry — (id, display_number, label, "Active"|"Locked")
MODULES = [
    ("m1", "01", "Problem Definition",    "Active"),
    ("m2", "02", "Feasibility Assessment", "Active"),
    ("m3", "03", "Gain–Pain Analysis",     "Locked"),
    ("m4", "04", "Governance Dashboard",   "Locked"),
]

# Sub-pages for each active module
M1_SUBPAGES = [
    ("chat",    "💬  AI Conversation"),
    ("extract", "📊  Extracted Info"),
    ("track",   "📈  Tracking"),
    ("log",     "🗂️  Submissions Log"),
]

M2_SUBPAGES = [
    ("select",     "🎯  Select Problem"),
    ("assess",     "🤖  AI Assessment"),
    ("results",    "📊  Results"),
    ("all_assess", "🗂️  All Assessments"),
]


def render_sidebar():
    with st.sidebar:
        _render_logo()
        _render_api_key()
        st.markdown("<hr style='border-color:#1e1d2e;margin:12px 0;'>", unsafe_allow_html=True)
        _render_module_nav()
        _render_sub_nav()
        st.markdown("<hr style='border-color:#1e1d2e;margin:12px 0;'>", unsafe_allow_html=True)
        _render_status_footer()


# ── Private helpers ───────────────────────────────────────────────────────────

def _render_logo():
    st.markdown("""
    <div style="padding:1.1rem 0.4rem 0.6rem;">
      <div style="font-size:1.05rem;font-weight:800;color:#fff;letter-spacing:0.01em;">🧠 AI Governance</div>
      <div style="font-size:0.68rem;color:#3a3a55;margin-top:2px;letter-spacing:0.04em;">ENTERPRISE PLATFORM</div>
    </div>""", unsafe_allow_html=True)


def _render_api_key():
    st.markdown('<div class="sbar-lbl">API Configuration</div>', unsafe_allow_html=True)
    stored = st.session_state.get("api_key_input", "")
    key_in = st.text_input(
        "Gemini API key", value=stored, type="password",
        placeholder="AIza...", label_visibility="collapsed",
        help="Get your key from aistudio.google.com",
    )
    if key_in:
        st.session_state["api_key_input"] = key_in
        st.markdown('<div style="font-size:0.72rem;color:#1D9E75;margin-top:-6px;">🔑 Key configured</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:0.72rem;color:#E24B4A;margin-top:-6px;">⚠ API key required</div>',
                    unsafe_allow_html=True)


def _render_module_nav():
    st.markdown('<div class="sbar-lbl">Modules</div>', unsafe_allow_html=True)
    for mid, num, mlabel, mstatus in MODULES:
        is_active = st.session_state.active_module == mid
        is_locked = mstatus == "Locked"
        css_cls   = "mod-active" if is_active else "mod-inactive"

        col_btn, col_badge = st.columns([5, 2])
        with col_btn:
            st.markdown(f'<div class="{css_cls}">', unsafe_allow_html=True)
            if st.button(f"{num}  {mlabel}", key=f"mod_{mid}",
                         use_container_width=True, disabled=is_locked):
                st.session_state.active_module = mid
                st.session_state.active_sub    = "chat"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with col_badge:
            if is_locked:
                st.markdown('<div style="font-size:0.62rem;color:#333;padding-top:10px;">🔒 Soon</div>',
                            unsafe_allow_html=True)
            elif is_active:
                st.markdown('<div style="font-size:0.62rem;color:#6C63FF;padding-top:10px;">● Active</div>',
                            unsafe_allow_html=True)


def _render_sub_nav():
    mod = st.session_state.active_module

    if mod == "m1":
        st.markdown("<hr style='border-color:#1e1d2e;margin:10px 0;'>", unsafe_allow_html=True)
        st.markdown('<div class="sbar-lbl">Problem Definition</div>', unsafe_allow_html=True)
        for sid, slabel in M1_SUBPAGES:
            _subnav_button(sid, slabel, state_key="active_sub")

    elif mod == "m2":
        st.markdown("<hr style='border-color:#1e1d2e;margin:10px 0;'>", unsafe_allow_html=True)
        st.markdown('<div class="sbar-lbl">Feasibility Assessment</div>', unsafe_allow_html=True)
        for sid, slabel in M2_SUBPAGES:
            _subnav_button(sid, slabel, state_key="m2_sub")


def _subnav_button(sid: str, label: str, state_key: str):
    is_active = st.session_state.get(state_key) == sid
    css = "subnav-active" if is_active else "subnav-inactive"
    st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
    if st.button(label, key=f"subnav_{sid}", use_container_width=True):
        st.session_state[state_key] = sid
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_status_footer():
    status  = st.session_state.current_status
    total   = len(st.session_state.submitted_records)
    bdg_map = {"draft": "b-draft", "complete": "b-ready", "submitted": "b-submitted"}
    lbl_map = {"draft": "Draft", "complete": "Ready to submit", "submitted": "Submitted"}
    bdg = bdg_map.get(status, "b-draft")
    lbl = lbl_map.get(status, "Draft")

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
      <span style="font-size:0.75rem;color:#444;">Status</span>
      <span class="badge {bdg}">{lbl}</span>
    </div>
    <div style="font-size:0.73rem;color:#444;">
      Total submissions: <strong style="color:#7effc8;">{total}</strong>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    if st.button("＋  New Problem Statement", use_container_width=True, key="new_prob"):
        for k in ["messages", "extracted", "current_status", "submission_id"]:
            st.session_state.pop(k, None)
        st.session_state.submitted_records = db_load_all()
        st.session_state.active_sub        = "chat"
        st.rerun()
