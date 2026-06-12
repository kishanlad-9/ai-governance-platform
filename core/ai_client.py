# core/ai_client.py
# ─────────────────────────────────────────────────────────────────────────────
# All Gemini API interactions live here.
# Swap the underlying model or provider by editing only this file.
# ─────────────────────────────────────────────────────────────────────────────

import os
import re
import json
import streamlit as st
import google.generativeai as genai

from config.constants  import REQUIRED_FIELDS
from config.prompts    import M1_SYSTEM_PROMPT, M2_SCORING_PROMPT, M2_REPORT_PROMPT
from config.dimensions import ASSESSMENT_DIMENSIONS

MODEL_NAME = "gemini-2.5-flash"


# ── API key resolution ────────────────────────────────────────────────────────

def get_api_key() -> str:
    """Resolve Gemini API key from Streamlit secrets → env vars → sidebar input."""
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


def _configure():
    """Configure the Gemini client; stop the app if no key is available."""
    key = get_api_key()
    if not key:
        st.error("Enter your Gemini API key in the sidebar to continue.")
        st.stop()
    genai.configure(api_key=key)


# ── Module 1 — intake conversation ───────────────────────────────────────────

def call_m1_ai(messages: list) -> str:
    """
    Send the full conversation history to Gemini and return the assistant reply.
    Injects a [MISSING FIELDS] hint so the model knows what to ask next.
    """
    _configure()
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=M1_SYSTEM_PROMPT,
    )

    # Build Gemini-format history (all messages except the last)
    history = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in messages[:-1]
    ]
    chat    = model.start_chat(history=history)
    missing = _get_missing_fields()
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


def _get_missing_fields() -> list:
    ext = st.session_state.get("extracted", {})
    return [
        label for key, label in REQUIRED_FIELDS
        if not ext.get(key) or ext.get(key) in ("null", "unknown", "TBD", "")
    ]


# ── Module 2 — AI scoring (returns structured scores) ────────────────────────

def call_m2_scoring(problem: dict) -> dict:
    """
    Ask the AI to score all 25 assessment criteria based on the problem statement.
    Returns a nested dict: {dimension_id: {question_id: score (1–5)}}.
    Returns {} on failure.
    """
    _configure()
    model = genai.GenerativeModel(model_name=MODEL_NAME)

    prompt = f"""PROBLEM STATEMENT:
- Problem: {problem.get('problem_statement', '')}
- Business Objective: {problem.get('business_objective', '')}
- Proposed Solution Approach: {problem.get('solution_approach', '')}
- Quantified Business Value: {problem.get('business_value', '')}
- Workflow / Process Location: {problem.get('workflow_location', '')}
- Decision Support Required: {problem.get('decision_support', '')}
- Timeline: {problem.get('timeline', '')}
- Action Owner: {problem.get('action_owner', '')}

{M2_SCORING_PROMPT}"""

    raw = model.generate_content(prompt).text.strip()
    # Strip accidental markdown fences
    raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
    try:
        return json.loads(raw)
    except Exception:
        return {}


# ── Module 2 — AI recommendation report ──────────────────────────────────────

def call_m2_report(problem: dict, scores: dict, responses: dict) -> str:
    """
    Generate a structured narrative feasibility report given scores and context.
    Returns the full markdown report as a string.
    """
    _configure()
    model = genai.GenerativeModel(model_name=MODEL_NAME)

    # Build a readable score breakdown for the prompt
    dim_lines = []
    for dim in ASSESSMENT_DIMENSIONS:
        s = scores.get(dim["id"], 0)
        dim_lines.append(f"  - {dim['label']} ({dim['role']}): {s:.1f}/5")
        for q_id, q_label in dim["questions"]:
            ans = responses.get(dim["id"], {}).get(q_id, 0)
            dim_lines.append(f"      • {q_label}: {ans}/5")

    overall = sum(scores.values()) / len(scores) if scores else 0
    verdict = _score_to_verdict(overall)

    prompt = f"""PROBLEM STATEMENT (from Module 1):
- Problem: {problem.get('problem_statement', '')}
- Objective: {problem.get('business_objective', '')}
- Solution approach: {problem.get('solution_approach', '')}
- Business value: {problem.get('business_value', '')}
- Workflow: {problem.get('workflow_location', '')}
- Timeline: {problem.get('timeline', '')}
- Owner: {problem.get('action_owner', '')}

FEASIBILITY SCORES:
{chr(10).join(dim_lines)}

Overall weighted score: {overall:.2f}/5
Verdict: {verdict}

{M2_REPORT_PROMPT}"""

    return model.generate_content(prompt).text


def _score_to_verdict(score: float) -> str:
    if score >= 3.5:
        return "Feasible"
    if score >= 2.5:
        return "Conditional"
    return "Not Feasible"
