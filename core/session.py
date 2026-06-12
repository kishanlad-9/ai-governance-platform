# core/session.py
# ─────────────────────────────────────────────────────────────────────────────
# Streamlit session state initialisation.
# All default keys live here so there is one source of truth.
# When adding state for a new module, add its defaults to SESSION_DEFAULTS.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
from config.constants import FIELD_KEYS
from core.database    import init_db, db_load_all


def init_session():
    """Initialise DB and seed any missing session-state keys with defaults."""
    init_db()

    defaults = {
        # ── App navigation ────────────────────────────────────────────────────
        "active_module": "m1",
        "active_sub":    "chat",

        # ── Module 1 — problem definition ────────────────────────────────────
        "messages":          [],
        "extracted":         {**{k: None for k in FIELD_KEYS},
                              "completeness_pct": 0,
                              "ready_to_submit":  False},
        "current_status":    "draft",
        "submission_id":     None,
        "submitted_records": db_load_all(),

        # ── Module 2 — feasibility assessment ────────────────────────────────
        "m2_sub":         "select",
        "m2_selected_id": None,
        "m2_responses":   {},
        "m2_scores":      {},
        "m2_submitted":   False,
        "m2_ai_reco":     "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
