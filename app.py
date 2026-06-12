# app.py  — entry point. Run: streamlit run app.py

import streamlit as st
from config.styles import STYLES
from config.constants import FIELD_KEYS
from database.db import init_db, db_load_all
from modules.sidebar import render_sidebar
from modules.module1 import chat
from modules.module2 import select as m2
from modules.module3 import gainpain as m3

st.set_page_config(page_title="AI Governance", page_icon="🧠",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown(STYLES, unsafe_allow_html=True)


def init_session():
    init_db()
    defaults = {
        # navigation
        "active_module":     "m1",
        # M1
        "messages":          [],
        "extracted":         {**{k: None for k in FIELD_KEYS}, "completeness_pct": 0, "ready_to_submit": False},
        "submitted_records": db_load_all(),
        "current_status":    "draft",
        "submission_id":     None,
        "m1_step":           "chat",
        # M2
        "m2_step":           "pick",
        "m2_selected_id":    None,
        "m2_responses":      {},
        "m2_dim_idx":        0,
        "m2_assessor":       "",
        "m2_ai_result":      None,
        # M3
        "m3_step":           "pick",
        "m3_selected_id":    None,
        "m3_ai_result":      None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def coming_soon(title, icon, note):
    st.markdown(f"""
    <div style="padding:2rem 0 1rem;">
      <h2 style="font-size:1.4rem;font-weight:700;color:#1a1a2e;margin-bottom:0.3rem;">{icon} {title}</h2>
    </div>
    <div class="coming-wrap">
      <div style="font-size:2.5rem;margin-bottom:0.8rem;">🚧</div>
      <h2>Coming soon</h2>
      <p style="font-size:0.85rem;color:#bbb;">{note}</p>
    </div>""", unsafe_allow_html=True)


def main():
    init_session()
    render_sidebar()

    mod = st.session_state.active_module
    if   mod == "m1": chat.render()
    elif mod == "m2": m2.render()
    elif mod == "m3": m3.render()
    elif mod == "m4": coming_soon("Governance Dashboard",  "📊",  "Unlocks after gain–pain analysis.")


if __name__ == "__main__":
    main()
