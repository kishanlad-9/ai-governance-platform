# utils/helpers.py
# Shared utility functions used across all modules

import re
import json
import os
import streamlit as st
import google.generativeai as genai

from config.constants import REQUIRED_FIELDS, FIELD_KEYS
from config.prompts import M1_SYSTEM_PROMPT


# ── API key resolution ────────────────────────────────────────────────────────
def get_api_key() -> str:
    """Check secrets → env vars → sidebar input, in that order."""
    for k in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        try:
            v = st.secrets[k]
            if v:
                return v
        except Exception:
            pass
    for k in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        v = os.environ.get(k, "")
        if v:
            return v
    return st.session_state.get("api_key_input", "")


# ── UI helpers ────────────────────────────────────────────────────────────────
def get_completeness_color(pct: int) -> str:
    """Return a colour hex based on percentage: red / amber / green."""
    if pct < 40:
        return "#E24B4A"
    if pct < 75:
        return "#EF9F27"
    return "#1D9E75"


def is_field_done(key: str) -> bool:
    """Return True if the extracted field has a real value."""
    v = st.session_state.extracted.get(key)
    return bool(v and v not in ("null", "unknown", "TBD", ""))


# ── JSON extraction helpers ───────────────────────────────────────────────────
def parse_extracted(text: str) -> dict | None:
    """Pull the hidden JSON block out of an AI response."""
    m = re.search(r"```json\s*([\s\S]*?)```", text)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def strip_json(text: str) -> str:
    """Remove the hidden JSON block before displaying to the user."""
    return re.sub(r"```json[\s\S]*?```", "", text).strip()


# ── Module 1 — AI conversation ────────────────────────────────────────────────
def get_missing_fields() -> list:
    """Return list of field labels still missing in the current session."""
    ext = st.session_state.get("extracted", {})
    return [
        label for key, label in REQUIRED_FIELDS
        if not ext.get(key) or ext.get(key) in ("null", "unknown", "TBD", "")
    ]


def call_m1_ai(messages: list) -> str:
    """Send the conversation to Gemini for Module 1 field extraction."""
    api_key = get_api_key()
    if not api_key:
        st.error("Enter your Gemini API key in the sidebar to start.")
        st.stop()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=M1_SYSTEM_PROMPT
    )
    history = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in messages[:-1]
    ]
    chat    = model.start_chat(history=history)
    missing = get_missing_fields()
    last    = messages[-1]["content"]

    if missing:
        injected = (
            "[MISSING FIELDS — ask about the FIRST one only]:\n"
            + "\n".join(f"- {m}" for m in missing)
            + f"\n\n[USER MESSAGE]:\n{last}"
        )
    else:
        injected = f"[ALL FIELDS COLLECTED — confirm summary now]\n\n[USER MESSAGE]:\n{last}"

    return chat.send_message(injected).text


# ── Module 2 — Feasibility AI call ───────────────────────────────────────────
def call_m2_ai(prompt: str) -> str:
    """Send a pre-built prompt to Gemini for Module 2 recommendation."""
    api_key = get_api_key()
    if not api_key:
        return "AI recommendation unavailable — no API key configured."
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    return model.generate_content(prompt).text


# ── Module 2 — AI-driven full assessment ──────────────────────────────────────
def call_m2_assessment(problem: dict) -> dict | None:
    """
    Send the problem statement to Gemini and get back a full structured
    feasibility assessment as a Python dict. Returns None on failure.
    """
    import json
    from config.prompts import M2_ASSESSMENT_PROMPT

    api_key = get_api_key()
    if not api_key:
        st.error("Enter your Gemini API key in the sidebar.")
        st.stop()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")

    prompt = f"""{M2_ASSESSMENT_PROMPT}

PROBLEM STATEMENT TO ASSESS:
- Business problem: {problem.get('problem_statement', '')}
- Business objective: {problem.get('business_objective', '')}
- Proposed solution: {problem.get('solution_approach', '')}
- Workflow / department: {problem.get('workflow_location', '')}
- Decision support needed: {problem.get('decision_support', '')}
- Timeline: {problem.get('timeline', '')}
- Action owner: {problem.get('action_owner', '')}
- Quantified business value: {problem.get('business_value', '')}

Analyse the above and return ONLY the JSON object as specified."""

    try:
        resp = model.generate_content(prompt)
        text = clean_llm_json(resp.text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        st.error(f"AI returned malformed JSON: {e}")
        st.code(resp.text[:800], language="json")
        return None
    except Exception as e:
        st.error(f"AI assessment failed: {e}")
        return None


# ── Robust JSON cleaner ───────────────────────────────────────────────────────
def clean_llm_json(text: str) -> str:
    """Strip markdown fences, trailing commas, and other LLM JSON quirks."""
    import re
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    # Remove trailing commas before } or ]
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text
