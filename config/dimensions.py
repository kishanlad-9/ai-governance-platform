# config/dimensions.py
# ─────────────────────────────────────────────────────────────────────────────
# Module 2 — Assessment dimensions, stakeholder roles, and scoring questions.
#
# Framework alignment:
#   ai_suitability    — original 5 + 2 new questions (NIST MAP 1.5, MAP 2.3)
#   economic_viability — unchanged (neither NIST nor ISO adds to this)
#   data_readiness    — original 5 + 3 new questions (NIST MAP 2.2, MEASURE 2.5, 2.7)
#   workflow_maturity  — original 5 + 1 new question  (NIST GOVERN 1.2)
#   change_management  — unchanged (ISO Clauses 7.2–7.4 already covered)
#   risk_compliance   — entirely NEW dimension         (NIST GOVERN 6.1 + ISO 6.1.3)
#
# Scoring scale (all questions):
#   1 = Strongly disagree / Not at all true / Not in place
#   2 = Disagree / Unlikely / Major gaps
#   3 = Neutral / Partially true / In progress
#   4 = Agree / Likely / Mostly in place
#   5 = Strongly agree / Definitely true / Fully in place
#
# Hard gate questions (verdict capped at Not Feasible if score ≤ 2):
#   data_readiness   → bias_risk            (NIST MAP 2.2)
#   risk_compliance  → regulatory_compliance (NIST GOVERN 6.1)
#
# To add a new dimension:
#   1. Add a dict entry here following the same schema.
#   2. Add the corresponding column to the DB table in core/database.py.
#   3. Update M2_SCORING_PROMPT in config/prompts.py.
# ─────────────────────────────────────────────────────────────────────────────

ASSESSMENT_DIMENSIONS = [

    # ── Dimension 1 — AI Suitability ─────────────────────────────────────────
    # Original 5 questions + 2 new NIST questions
    # NIST MAP 1.5 → autonomous_decision_level
    # NIST MAP 2.3 → failure_impact_severity
    {
        "id":    "ai_suitability",
        "label": "AI Suitability",
        "icon":  "🤖",
        "role":  "Process Owner",
        "color": "#6C63FF",
        "framework": "NIST MAP 1.1 / MAP 1.5 / MAP 2.3",
        "desc":  "Evaluates whether the problem is genuinely suitable for AI vs rules/traditional approaches. "
                 "Includes NIST-required assessment of autonomy level and failure severity.",
        "questions": [
            # ── Original questions ────────────────────────────────────────────
            ("pattern_complexity",      "The problem involves complex patterns that are difficult to express as simple rules"),
            ("data_driven",             "The problem is inherently data-driven and has variability that rules cannot fully capture"),
            ("ai_over_rules",           "AI would provide measurable advantages over rule-based or traditional ML approaches"),
            ("repeatability",           "The problem occurs frequently enough to justify AI development and maintenance cost"),
            ("outcome_clarity",         "The desired outcome/output of the AI system is clearly definable and measurable"),
            # ── NIST MAP 1.5 — Organisational risk tolerances ─────────────────
            # Score meaning is INVERTED here: 1=fully autonomous (high risk),
            # 5=advisory only (low risk). Higher score = safer autonomy level.
            ("autonomous_decision_level",
             "The AI system acts in an advisory capacity only — a human makes all final decisions "
             "(score LOW if the AI makes autonomous irreversible decisions with no human override)"),
            # ── NIST MAP 2.3 — Scientific findings and AI limitations ─────────
            # Score meaning is INVERTED: 1=catastrophic failure impact, 5=negligible.
            ("failure_impact_severity",
             "If this AI system produces a wrong output, the impact on affected people or processes "
             "is low and easily corrected "
             "(score LOW if a wrong output causes serious harm, legal exposure, or irreversible damage)"),
        ],
    },

    # ── Dimension 2 — Economic Viability ─────────────────────────────────────
    # Unchanged — neither NIST nor ISO provides a scoring methodology here
    {
        "id":    "economic_viability",
        "label": "Economic Viability",
        "icon":  "💰",
        "role":  "Finance / Business Lead",
        "color": "#0F6E56",
        "framework": "Internal (Gartner Business Value axis reference)",
        "desc":  "Assesses ROI potential, cost of implementation, and scale benefits.",
        "questions": [
            ("roi_potential",       "The projected ROI or cost savings justifies the investment in AI development"),
            ("scale_benefit",       "The solution will deliver increasing returns as it scales across the organisation"),
            ("budget_availability", "Adequate budget is available or can be allocated for this initiative"),
            ("time_to_value",       "The time to realise business value is acceptable given the investment required"),
            ("competitive_edge",    "Implementing this AI solution provides a meaningful competitive or operational advantage"),
        ],
    },

    # ── Dimension 3 — Data & Technology Readiness ────────────────────────────
    # Original 5 questions + 3 new NIST questions
    # NIST MAP 2.2   → bias_risk            ← HARD GATE question
    # NIST MEASURE 2.5 → explainability
    # NIST MEASURE 2.7 → monitoring_plan
    {
        "id":    "data_readiness",
        "label": "Data & Technology Readiness",
        "icon":  "🗄️",
        "role":  "Data / Technology Team",
        "color": "#C07A10",
        "framework": "NIST MAP 2.2 / MEASURE 2.5 / MEASURE 2.7 + ISO Annex A.8",
        "desc":  "Checks data availability, quality, infrastructure, and technology stack readiness. "
                 "Includes NIST-required bias audit, explainability assessment, and monitoring plan. "
                 "⚠️ bias_risk is a hard gate — a score of 1 or 2 caps the overall verdict at Not Feasible.",
        "questions": [
            # ── Original questions ────────────────────────────────────────────
            ("data_availability", "Sufficient historical data exists or can be collected to train and validate the AI model"),
            ("data_quality",      "The available data is of acceptable quality (accurate, complete, consistent)"),
            ("infrastructure",    "The technology infrastructure required to deploy and run this AI solution is in place"),
            ("integration_ease",  "The AI solution can be integrated into existing systems and workflows without major re-engineering"),
            ("data_governance",   "Data privacy, security, and governance requirements can be met for this use case"),
            # ── NIST MAP 2.2 — Scientific findings on AI biases — HARD GATE ──
            ("bias_risk",
             "The training data has been evaluated for historical bias and discriminatory patterns, "
             "and a mitigation plan is in place where bias is identified "
             "(⚠️ HARD GATE — score of 1 or 2 blocks a Feasible verdict regardless of overall score)"),
            # ── NIST MEASURE 2.5 — Explainability and interpretability ────────
            ("explainability",
             "The AI system can explain its decisions or recommendations in plain language "
             "to a non-technical person, including the individual affected by the decision"),
            # ── NIST MEASURE 2.7 — AI system performance monitoring ───────────
            ("monitoring_plan",
             "A defined plan exists for monitoring this AI system's performance after deployment, "
             "including detection of model drift and defined alert thresholds with named owners"),
        ],
    },

    # ── Dimension 4 — Workflow Maturity ──────────────────────────────────────
    # Original 5 questions + 1 new NIST question
    # NIST GOVERN 1.2 → human_in_loop
    {
        "id":    "workflow_maturity",
        "label": "Workflow Maturity",
        "icon":  "⚙️",
        "role":  "Operations / Process Owner",
        "color": "#8B2FC9",
        "framework": "ISO 42001 Clause 8.1 / 8.3 + NIST GOVERN 1.2",
        "desc":  "Evaluates how well-defined and stable the current process is for AI augmentation. "
                 "Includes NIST-required human-in-the-loop checkpoint assessment.",
        "questions": [
            # ── Original questions ────────────────────────────────────────────
            ("process_defined",    "The current process/workflow is well-documented and clearly defined"),
            ("process_stable",     "The process is stable and not undergoing major changes that would affect AI training"),
            ("exception_handling", "Edge cases and exceptions in the process are understood and manageable"),
            ("kpi_defined",        "Clear KPIs exist to measure success and monitor AI performance post-deployment"),
            ("ownership_clear",    "Process ownership and accountability for the AI-augmented workflow is clearly assigned"),
            # ── NIST GOVERN 1.2 — Policies for human oversight ───────────────
            ("human_in_loop",
             "There is a defined and documented point in the workflow where a human reviews or validates "
             "the AI output before it results in a consequential action or decision "
             "(score LOW if AI output directly triggers automated actions with no human checkpoint)"),
        ],
    },

    # ── Dimension 5 — Change Management ──────────────────────────────────────
    # Unchanged — ISO Clauses 7.2, 7.3, 7.4 and NIST GOVERN 4.1 are already
    # fully covered by the existing 5 questions
    {
        "id":    "change_management",
        "label": "Change Management",
        "icon":  "👥",
        "role":  "HR / Change Management",
        "color": "#C0392B",
        "framework": "ISO 42001 Clauses 7.2 / 7.3 / 7.4 / 5.1",
        "desc":  "Assesses organisational readiness, adoption risk, and people-related challenges. "
                 "Fully aligned with ISO 42001 competence, awareness, and leadership requirements.",
        "questions": [
            ("leadership_support",   "Senior leadership actively supports and champions this AI initiative"),
            ("user_acceptance",      "End users are likely to accept and trust AI-assisted decision-making in this area"),
            ("training_feasibility", "Training and upskilling programs for impacted staff are feasible within the timeline"),
            ("resistance_risk",      "The risk of significant employee resistance or pushback is low and manageable"),
            ("culture_readiness",    "The organisational culture is ready to embrace AI-augmented processes"),
        ],
    },

    # ── Dimension 6 — Risk & Compliance (NEW) ────────────────────────────────
    # Entirely new dimension — did not exist before
    # NIST GOVERN 6.1 → regulatory_compliance  ← HARD GATE question
    # NIST MAP 5.1    → ethical_risk
    # NIST GOVERN 6.2 → audit_trail_feasibility
    # NIST MAP 1.1    → third_party_risk
    # ISO Clause 6.1.3 → legal_liability_clarity
    {
        "id":    "risk_compliance",
        "label": "Risk & Compliance",
        "icon":  "⚖️",
        "role":  "Legal / Compliance / Risk Team",
        "color": "#1A4A8A",
        "framework": "NIST GOVERN 6.1 / MAP 5.1 / GOVERN 6.2 / MAP 1.1 + ISO 42001 Clause 6.1.3",
        "desc":  "Assesses regulatory compliance, ethical risk, audit trail feasibility, third-party risk, "
                 "and legal liability clarity. "
                 "⚠️ regulatory_compliance is a hard gate — a score of 1 or 2 blocks any approval "
                 "regardless of overall score.",
        "questions": [
            # ── NIST GOVERN 6.1 — Regulatory compliance — HARD GATE ──────────
            ("regulatory_compliance",
             "The use case complies with all applicable laws and regulations including GDPR, "
             "sector-specific regulations (finance, healthcare, employment law) and organisational policy "
             "(⚠️ HARD GATE — score of 1 or 2 blocks any Approved verdict regardless of overall score)"),
            # ── NIST MAP 5.1 — Benefits and costs across all stakeholders ─────
            ("ethical_risk",
             "The AI system does not create unacceptable ethical risks such as discrimination, "
             "manipulation, erosion of individual rights, or disproportionate harm to vulnerable groups"),
            # ── NIST GOVERN 6.2 — Policies for AI transparency ───────────────
            ("audit_trail_feasibility",
             "It is technically and operationally feasible to maintain a complete, tamper-evident audit trail "
             "of all AI decisions for the required legal retention period"),
            # ── NIST MAP 1.1 — Context establishment ─────────────────────────
            ("third_party_risk",
             "Any third-party AI tools, models, APIs, or data providers involved in this system "
             "meet the organisation's vendor risk management and data security standards"),
            # ── ISO 42001 Clause 6.1.3 — Legal and regulatory requirements ───
            ("legal_liability_clarity",
             "The legal liability for incorrect, harmful, or discriminatory AI outputs is clearly defined "
             "and addressed by existing organisational policy, contracts, or insurance coverage"),
        ],
    },
]

