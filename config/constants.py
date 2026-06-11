# config/constants.py

# ── Module 1 — Problem Definition (13 fields: 8 original + 5 ISO 42001) ───────
REQUIRED_FIELDS = [
    # Original 8
    ("problem_statement",  "Business problem statement"),
    ("business_objective", "Business objective"),
    ("solution_approach",  "Proposed solution approach"),
    ("timeline",           "Timeline / deadline"),
    ("action_owner",       "Action owner / sponsor"),
    ("workflow_location",  "Workflow / process location"),
    ("decision_support",   "Decision support required"),
    ("business_value",     "Quantified business value"),
    # ISO 42001 additions
    ("iso_risk_category",     "ISO Risk Category"),           # ISO Clause 6.1.2
    ("affected_stakeholders", "Affected stakeholders"),       # ISO Clause 6.1.4
    ("human_override",        "Human oversight & override"),  # ISO Clause 8.4.3
    ("data_sources",          "Data sources & personal data"),# ISO Annex A.8
    ("success_criteria",      "AI success criteria & KPIs"),  # ISO Clause 6.2
]
FIELD_KEYS   = [f[0] for f in REQUIRED_FIELDS]
FIELD_LABELS = {f[0]: f[1] for f in REQUIRED_FIELDS}

ISO_RISK_LEVELS = ["Minimal", "Limited", "High", "Unacceptable"]

# ── Status ─────────────────────────────────────────────────────────────────────
STATUS_OPTIONS = ["Submitted", "Under Review", "Approved", "Rejected", "Deferred"]
STATUS_BADGE   = {
    "Submitted":    "b-submitted",
    "Under Review": "b-review",
    "Approved":     "b-approved",
    "Rejected":     "b-rejected",
    "Deferred":     "b-deferred",
}

# ── Module 2 — Feasibility Assessment (6 dimensions, 37 questions) ─────────────
# Updated per NIST AI RMF: 2 new Qs in AI Suitability, 3 new in Data Readiness,
# 1 new in Workflow Maturity, 1 entirely new Risk & Compliance dimension
ASSESSMENT_DIMENSIONS = [
    {
        "id":    "ai_suitability",
        "label": "AI Suitability",
        "icon":  "🤖",
        "role":  "Process Owner",
        "color": "#6C63FF",
        "desc":  "Evaluates whether the problem is genuinely suitable for AI. Includes NIST MAP assessment of autonomy level and failure severity.",
        "questions": [
            ("pattern_complexity",       "The problem involves complex patterns that are difficult to express as simple rules"),
            ("data_driven",              "The problem is data-driven with variability that rules cannot fully capture"),
            ("ai_over_rules",            "AI would provide measurable advantages over rule-based or traditional ML approaches"),
            ("repeatability",            "The problem occurs frequently enough to justify AI development and maintenance cost"),
            ("outcome_clarity",          "The desired AI output is clearly definable and measurable"),
            # NIST MAP 1.5
            ("autonomous_decision_level","The AI system acts as an advisor only — a human makes every final decision (1=fully autonomous, 5=advisory only)"),
            # NIST MAP 2.3
            ("failure_impact_severity",  "If the AI produces a wrong output, the impact on people and processes is low and easily corrected (1=catastrophic, 5=negligible)"),
        ],
    },
    {
        "id":    "economic_viability",
        "label": "Economic Viability",
        "icon":  "💰",
        "role":  "Finance / Business Lead",
        "color": "#0F6E56",
        "desc":  "Assesses ROI potential, cost of implementation, and scale benefits. Unchanged — existing questions satisfy framework requirements.",
        "questions": [
            ("roi_potential",       "The projected ROI or cost savings justifies the investment in AI development"),
            ("scale_benefit",       "The solution will deliver increasing returns as it scales across the organisation"),
            ("budget_availability", "Adequate budget is available or can be allocated for this initiative"),
            ("time_to_value",       "The time to realise business value is acceptable given the investment required"),
            ("competitive_edge",    "Implementing this AI solution provides a meaningful competitive or operational advantage"),
        ],
    },
    {
        "id":    "data_readiness",
        "label": "Data & Technology Readiness",
        "icon":  "🗄️",
        "role":  "Data / Technology Team",
        "color": "#C07A10",
        "desc":  "Checks data availability, quality, and infrastructure. Expanded with NIST MEASURE requirements for bias, explainability, and monitoring.",
        "questions": [
            ("data_availability",  "Sufficient historical data exists or can be collected to train and validate the AI model"),
            ("data_quality",       "The available data is accurate, complete, and consistent"),
            ("infrastructure",     "The technology infrastructure required to deploy and run this AI solution is in place"),
            ("integration_ease",   "The AI solution can be integrated into existing systems without major re-engineering"),
            ("data_governance",    "Data privacy, security, and governance requirements can be met for this use case"),
            # NIST MAP 2.2
            ("bias_risk",          "The training data has been evaluated for historical bias and mitigations are in place (1=no audit done/known biases, 5=formal audit completed)"),
            # NIST MEASURE 2.5
            ("explainability",     "The AI system can explain its decisions in plain language to the person affected by them (1=black box, 5=full plain-language explanations)"),
            # NIST MEASURE 2.7
            ("monitoring_plan",    "A defined post-deployment monitoring plan exists, including drift detection and alert owners (1=no plan, 5=automated monitoring with thresholds)"),
        ],
    },
    {
        "id":    "workflow_maturity",
        "label": "Workflow Maturity",
        "icon":  "⚙️",
        "role":  "Operations / Process Owner",
        "color": "#8B2FC9",
        "desc":  "Evaluates how well-defined the process is for AI augmentation. Expanded with NIST GOVERN requirement for human-in-the-loop integration.",
        "questions": [
            ("process_defined",    "The current process/workflow is well-documented and clearly defined"),
            ("process_stable",     "The process is stable and not undergoing major changes that would affect AI training"),
            ("exception_handling", "Edge cases and exceptions in the process are understood and manageable"),
            ("kpi_defined",        "Clear KPIs exist to measure success and monitor AI performance post-deployment"),
            ("ownership_clear",    "Process ownership and accountability for the AI-augmented workflow is clearly assigned"),
            # NIST GOVERN 1.2
            ("human_in_loop",     "There is a defined, documented human review step before any AI output results in a consequential action (1=no checkpoint, 5=human reviews every decision)"),
        ],
    },
    {
        "id":    "change_management",
        "label": "Change Management",
        "icon":  "👥",
        "role":  "HR / Change Management",
        "color": "#C0392B",
        "desc":  "Assesses organisational readiness and adoption risk. Unchanged — existing questions satisfy ISO 7.2, 7.3, 7.4 requirements.",
        "questions": [
            ("leadership_support",   "Senior leadership actively supports and champions this AI initiative"),
            ("user_acceptance",      "End users are likely to accept and trust AI-assisted decision-making in this area"),
            ("training_feasibility", "Training and upskilling programs for impacted staff are feasible within the timeline"),
            ("resistance_risk",      "The risk of significant employee resistance or pushback is low and manageable"),
            ("culture_readiness",    "The organisational culture is ready to embrace AI-augmented processes"),
        ],
    },
    {
        "id":    "risk_compliance",
        "label": "Risk & Compliance",
        "icon":  "⚖️",
        "role":  "Legal / Compliance / Risk Team",
        "color": "#1A5276",
        "desc":  "NEW dimension per NIST GOVERN + ISO 42001 Clause 6.1.3. Assesses regulatory compliance, ethical risk, audit trail feasibility, and legal liability.",
        "questions": [
            # NIST MAP 1.1 + ISO 6.1.3
            ("regulatory_compliance",   "The use case complies with all applicable laws and regulations (GDPR, sector-specific rules, employment law)"),
            # NIST GOVERN 6.1
            ("ethical_risk",            "The AI system does not create unacceptable ethical risks such as discrimination, manipulation, or violation of individual rights"),
            # NIST MAP 5.1
            ("audit_trail_feasibility", "It is technically feasible to create and maintain a complete audit trail of all AI decisions for the required retention period"),
            ("third_party_risk",        "Any third-party AI tools, models, or data providers involved meet the organisation's risk and compliance standards"),
            ("legal_liability_clarity", "Legal liability for incorrect or harmful AI outputs is clearly defined and covered by existing policy or insurance"),
        ],
    },
]

# Hard gate fields — a score of 1 or 2 on these blocks Feasible verdict
HARD_GATE_QUESTIONS = [
    ("data_readiness",  "bias_risk",             "Unmitigated training data bias detected"),
    ("risk_compliance", "regulatory_compliance",  "Potential regulatory non-compliance"),
]

VERDICT_CONFIG = {
    "Feasible":     {"color": "#1D9E75", "bg": "#D1F5EA", "icon": "✅"},
    "Conditional":  {"color": "#C07A10", "bg": "#FFF3CD", "icon": "⚠️"},
    "Not Feasible": {"color": "#C0392B", "bg": "#FDE8E8", "icon": "❌"},
}

# ── Module nav ─────────────────────────────────────────────────────────────────
MODULES = [
    ("m1", "01", "Problem Definition",    "Active"),
    ("m2", "02", "Feasibility Assessment", "Active"),
    ("m3", "03", "Gain–Pain Analysis",     "Locked"),
    ("m4", "04", "Governance Dashboard",   "Locked"),
]
