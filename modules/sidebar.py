# modules/sidebar.py
import streamlit as st
from config.constants import MODULES
from database.db import db_load_all


def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="padding:1.4rem 0.5rem 1rem;">
          <div style="font-size:1rem;font-weight:800;color:#fff;letter-spacing:0.01em;">🧠 AI Governance</div>
          <div style="font-size:0.68rem;color:#2a2940;margin-top:3px;letter-spacing:0.05em;">ENTERPRISE PLATFORM</div>
        </div>""", unsafe_allow_html=True)

        # API Key
        stored = st.session_state.get("api_key_input", "")
        key_in = st.text_input("API Key", value=stored, type="password",
                               placeholder="Gemini API key…", label_visibility="collapsed")
        if key_in:
            st.session_state["api_key_input"] = key_in
            from utils.helpers import detect_provider, resolve_model
            provider = detect_provider(key_in)
            icons = {"gemini": "♊", "openai": "⬡", "anthropic": "✦", "unknown": "?"}
            icon  = icons.get(provider, "?")
            if provider != "unknown":
                _, model = resolve_model(key_in)
                st.markdown(
                    f'<div style="font-size:0.7rem;color:#1D9E75;margin-top:-4px;padding-left:4px;">' +
                    f'● {icon} {provider.title()} · {model}</div>',
                    unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.7rem;color:#E24B4A;margin-top:-4px;padding-left:4px;">⚠ Unrecognised key format</div>',
                            unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:0.7rem;color:#E24B4A;margin-top:-4px;padding-left:4px;">● API key required</div>',
                        unsafe_allow_html=True)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # Module nav — 4 items only
        for mid, num, mlabel, mstatus in MODULES:
            is_active = st.session_state.active_module == mid
            is_locked = mstatus == "Locked"
            css = "mod-btn-active" if is_active else ("mod-btn-locked" if is_locked else "mod-btn-inactive")
            icon = "🔒 " if is_locked else ""
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            if st.button(f"{icon}{num}  {mlabel}", key=f"mod_{mid}",
                         use_container_width=True, disabled=is_locked):
                st.session_state.active_module = mid
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # New problem button at bottom
        st.markdown("<div style='position:absolute;bottom:1.5rem;left:1rem;right:1rem;'>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1a1929;margin-bottom:12px;'>", unsafe_allow_html=True)
        if st.button("＋  New Problem", use_container_width=True, key="new_prob"):
            for k in ["messages", "extracted", "current_status", "submission_id", "m1_step"]:
                st.session_state.pop(k, None)
            st.session_state.submitted_records = db_load_all()
            st.session_state.active_module = "m1"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
