# database/db.py — All SQLite operations

import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "ai_governance.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()

    # Module 1 — 13 fields (8 original + 5 ISO 42001)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS problem_statements (
            id                   TEXT PRIMARY KEY,
            submitted_at         TEXT,
            status               TEXT,
            problem_statement    TEXT,
            business_objective   TEXT,
            solution_approach    TEXT,
            timeline             TEXT,
            action_owner         TEXT,
            workflow_location    TEXT,
            decision_support     TEXT,
            business_value       TEXT,
            iso_risk_category    TEXT,
            affected_stakeholders TEXT,
            human_override       TEXT,
            data_sources         TEXT,
            success_criteria     TEXT
        )
    """)

    # Migrate existing DB — add new columns if they don't exist yet
    existing = [r[1] for r in conn.execute("PRAGMA table_info(problem_statements)").fetchall()]
    for col in ["iso_risk_category", "affected_stakeholders", "human_override",
                "data_sources", "success_criteria"]:
        if col not in existing:
            conn.execute(f"ALTER TABLE problem_statements ADD COLUMN {col} TEXT")

    # Module 2 — 6 dimensions (5 original + risk_compliance)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feasibility_assessments (
            id                       TEXT PRIMARY KEY,
            problem_id               TEXT,
            assessed_at              TEXT,
            assessor_name            TEXT,
            ai_suitability_score     REAL,
            economic_viability_score REAL,
            data_readiness_score     REAL,
            workflow_maturity_score  REAL,
            change_management_score  REAL,
            risk_compliance_score    REAL,
            hard_gate_triggered      INTEGER DEFAULT 0,
            hard_gate_reason         TEXT,
            overall_score            REAL,
            verdict                  TEXT,
            ai_recommendation        TEXT,
            responses                TEXT,
            FOREIGN KEY (problem_id) REFERENCES problem_statements(id)
        )
    """)

    # Migrate existing assessments table
    existing2 = [r[1] for r in conn.execute("PRAGMA table_info(feasibility_assessments)").fetchall()]
    for col, typ in [("risk_compliance_score","REAL"), ("hard_gate_triggered","INTEGER"),
                     ("hard_gate_reason","TEXT")]:
        if col not in existing2:
            conn.execute(f"ALTER TABLE feasibility_assessments ADD COLUMN {col} {typ}")

    init_m3_table(conn)
    conn.commit()
    conn.close()


# ── Module 1 ───────────────────────────────────────────────────────────────────

def db_insert_record(record: dict):
    conn = get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO problem_statements
        (id, submitted_at, status,
         problem_statement, business_objective, solution_approach,
         timeline, action_owner, workflow_location, decision_support, business_value,
         iso_risk_category, affected_stakeholders, human_override,
         data_sources, success_criteria)
        VALUES
        (:id, :submitted_at, :status,
         :problem_statement, :business_objective, :solution_approach,
         :timeline, :action_owner, :workflow_location, :decision_support, :business_value,
         :iso_risk_category, :affected_stakeholders, :human_override,
         :data_sources, :success_criteria)
    """, record)
    conn.commit()
    conn.close()


def db_load_all() -> list:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM problem_statements ORDER BY submitted_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_update_status(record_id: str, new_status: str):
    conn = get_conn()
    conn.execute("UPDATE problem_statements SET status=? WHERE id=?", (new_status, record_id))
    conn.commit()
    conn.close()


def db_search(query: str) -> list:
    conn = get_conn()
    q = f"%{query.strip()}%"
    rows = conn.execute("""
        SELECT * FROM problem_statements
        WHERE id LIKE ? OR problem_statement LIKE ? OR business_objective LIKE ?
           OR action_owner LIKE ? OR iso_risk_category LIKE ?
        ORDER BY submitted_at DESC
    """, (q, q, q, q, q)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Module 2 ───────────────────────────────────────────────────────────────────

def db_save_assessment(rec: dict):
    conn = get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO feasibility_assessments
        (id, problem_id, assessed_at, assessor_name,
         ai_suitability_score, economic_viability_score, data_readiness_score,
         workflow_maturity_score, change_management_score, risk_compliance_score,
         hard_gate_triggered, hard_gate_reason,
         overall_score, verdict, ai_recommendation, responses)
        VALUES
        (:id, :problem_id, :assessed_at, :assessor_name,
         :ai_suitability_score, :economic_viability_score, :data_readiness_score,
         :workflow_maturity_score, :change_management_score, :risk_compliance_score,
         :hard_gate_triggered, :hard_gate_reason,
         :overall_score, :verdict, :ai_recommendation, :responses)
    """, rec)
    conn.commit()
    conn.close()


def db_load_assessments(problem_id: str = None) -> list:
    conn = get_conn()
    if problem_id:
        rows = conn.execute(
            "SELECT * FROM feasibility_assessments WHERE problem_id=? ORDER BY assessed_at DESC",
            (problem_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM feasibility_assessments ORDER BY assessed_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Module 3 — Gain Pain Analysis ─────────────────────────────────────────────

def init_m3_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gainpain_analyses (
            id                     TEXT PRIMARY KEY,
            problem_id             TEXT,
            assessment_id          TEXT,
            analysed_at            TEXT,
            business_value_gain    REAL,
            strategic_alignment    REAL,
            efficiency_gain        REAL,
            innovation_potential   REAL,
            implementation_cost    REAL,
            operational_risk       REAL,
            adoption_resistance    REAL,
            compliance_burden      REAL,
            avg_gains              REAL,
            avg_pains              REAL,
            priority_score         REAL,
            priority_score_scaled  REAL,
            priority_band          TEXT,
            ai_analysis            TEXT,
            FOREIGN KEY (problem_id) REFERENCES problem_statements(id)
        )
    """)


def db_save_gainpain(rec: dict):
    conn = get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO gainpain_analyses
        (id, problem_id, assessment_id, analysed_at,
         business_value_gain, strategic_alignment, efficiency_gain, innovation_potential,
         implementation_cost, operational_risk, adoption_resistance, compliance_burden,
         avg_gains, avg_pains, priority_score, priority_score_scaled, priority_band, ai_analysis)
        VALUES
        (:id, :problem_id, :assessment_id, :analysed_at,
         :business_value_gain, :strategic_alignment, :efficiency_gain, :innovation_potential,
         :implementation_cost, :operational_risk, :adoption_resistance, :compliance_burden,
         :avg_gains, :avg_pains, :priority_score, :priority_score_scaled, :priority_band, :ai_analysis)
    """, rec)
    conn.commit()
    conn.close()


def db_load_gainpain(problem_id: str = None) -> list:
    conn = get_conn()
    if problem_id:
        rows = conn.execute(
            "SELECT * FROM gainpain_analyses WHERE problem_id=? ORDER BY analysed_at DESC",
            (problem_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM gainpain_analyses ORDER BY analysed_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
