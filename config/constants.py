# config/constants.py
# All shared constants used across modules

# ── Module 1 — Problem Definition ─────────────────────────────────────────────
REQUIRED_FIELDS = [
    ("problem_statement",  "Business problem statement"),
    ("business_objective", "Business objective"),
    ("solution_approach",  "Proposed solution approach"),
    ("timeline",           "Timeline / deadline"),
    ("action_owner",       "Action owner / sponsor"),
    ("workflow_location",  "Workflow / process location"),
    ("decision_support",   "Decision support required"),
    ("business_value",     "Quantified business value"),
]
FIELD_KEYS   = [f[0] for f in REQUIRED_FIELDS]
FIELD_LABELS = {f[0]: f[1] for f in REQUIRED_FIELDS}

# ── Status options & badge CSS classes ────────────────────────────────────────
STATUS_OPTIONS = ["Submitted", "Under Review", "Approved", "Rejected", "Deferred"]
STATUS_BADGE   = {
    "Submitted":    "b-submitted",
    "Under Review": "b-review",
    "Approved":     "b-approved",
    "Rejected":     "b-rejected",
    "Deferred":     "b-deferred",
}

# ── Module 2 — Feasibility Assessment ─────────────────────────────────────────
ASSESSMENT_DIMENSIONS = [
    {
        "id":    "ai_suitability",
        "label": "AI Suitability",
        "icon":  "🤖",
        "role":  "Process Owner",
        "color": "#6C63FF",
        "desc":  "Evaluates whether the problem is genuinely suitable for AI vs rules/traditional approaches.",
        "questions": [
            ("pattern_complexity",  "The problem involves complex patterns that are difficult to express as simple rules"),
            ("data_driven",         "The problem is inherently data-driven and has variability that rules cannot fully capture"),
            ("ai_over_rules",       "AI would provide measurable advantages over rule-based or traditional ML approaches"),
            ("repeatability",       "The problem occurs frequently enough to justify AI development and maintenance cost"),
            ("outcome_clarity",     "The desired outcome/output of the AI system is clearly definable and measurable"),
        ],
    },
    {
        "id":    "economic_viability",
        "label": "Economic Viability",
        "icon":  "💰",
        "role":  "Finance / Business Lead",
        "color": "#0F6E56",
        "desc":  "Assesses ROI potential, cost of implementation, and scale benefits.",
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
        "desc":  "Checks data availability, quality, infrastructure, and technology stack readiness.",
        "questions": [
            ("data_availability",   "Sufficient historical data exists or can be collected to train and validate the AI model"),
            ("data_quality",        "The available data is of acceptable quality (accurate, complete, consistent)"),
            ("infrastructure",      "The technology infrastructure required to deploy and run this AI solution is in place"),
            ("integration_ease",    "The AI solution can be integrated into existing systems and workflows without major re-engineering"),
            ("data_governance",     "Data privacy, security, and governance requirements can be met for this use case"),
        ],
    },
    {
        "id":    "workflow_maturity",
        "label": "Workflow Maturity",
        "icon":  "⚙️",
        "role":  "Operations / Process Owner",
        "color": "#8B2FC9",
        "desc":  "Evaluates how well-defined and stable the current process is for AI augmentation.",
        "questions": [
            ("process_defined",    "The current process/workflow is well-documented and clearly defined"),
            ("process_stable",     "The process is stable and not undergoing major changes that would affect AI training"),
            ("exception_handling", "Edge cases and exceptions in the process are understood and manageable"),
            ("kpi_defined",        "Clear KPIs exist to measure success and monitor AI performance post-deployment"),
            ("ownership_clear",    "Process ownership and accountability for the AI-augmented workflow is clearly assigned"),
        ],
    },
    {
        "id":    "change_management",
        "label": "Change Management",
        "icon":  "👥",
        "role":  "HR / Change Management",
        "color": "#C0392B",
        "desc":  "Assesses organisational readiness, adoption risk, and people-related challenges.",
        "questions": [
            ("leadership_support",   "Senior leadership actively supports and champions this AI initiative"),
            ("user_acceptance",      "End users are likely to accept and trust AI-assisted decision-making in this area"),
            ("training_feasibility", "Training and upskilling programs for impacted staff are feasible within the timeline"),
            ("resistance_risk",      "The risk of significant employee resistance or pushback is low and manageable"),
            ("culture_readiness",    "The organisational culture is ready to embrace AI-augmented processes"),
        ],
    },
]

VERDICT_CONFIG = {
    "Feasible":     {"color": "#1D9E75", "bg": "#D1F5EA", "icon": "✅"},
    "Conditional":  {"color": "#C07A10", "bg": "#FFF3CD", "icon": "⚠️"},
    "Not Feasible": {"color": "#C0392B", "bg": "#FDE8E8", "icon": "❌"},
}

# ── Module nav definition ──────────────────────────────────────────────────────
MODULES = [
    ("m1", "01", "Problem Definition",    "Active"),
    ("m2", "02", "Feasibility Assessment", "Active"),
    ("m3", "03", "Gain–Pain Analysis",     "Locked"),
    ("m4", "04", "Governance Dashboard",   "Locked"),
]
