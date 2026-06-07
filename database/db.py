# database/db.py
# All SQLite database operations — one place for all data access

import sqlite3

DB_PATH = "ai_governance.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables on first run. Safe to call on every startup."""
    conn = get_conn()

    # Module 1 — Problem statements
    conn.execute("""
        CREATE TABLE IF NOT EXISTS problem_statements (
            id                 TEXT PRIMARY KEY,
            submitted_at       TEXT,
            status             TEXT,
            problem_statement  TEXT,
            business_objective TEXT,
            solution_approach  TEXT,
            timeline           TEXT,
            action_owner       TEXT,
            workflow_location  TEXT,
            decision_support   TEXT,
            business_value     TEXT
        )
    """)

    # Module 2 — Feasibility assessments
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
            overall_score            REAL,
            verdict                  TEXT,
            ai_recommendation        TEXT,
            responses                TEXT,
            FOREIGN KEY (problem_id) REFERENCES problem_statements(id)
        )
    """)

    conn.commit()
    conn.close()


# ── Module 1 — Problem statements ─────────────────────────────────────────────

def db_insert_record(record: dict):
    conn = get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO problem_statements
        (id, submitted_at, status, problem_statement, business_objective,
         solution_approach, timeline, action_owner, workflow_location,
         decision_support, business_value)
        VALUES (:id, :submitted_at, :status, :problem_statement, :business_objective,
                :solution_approach, :timeline, :action_owner, :workflow_location,
                :decision_support, :business_value)
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
    conn.execute(
        "UPDATE problem_statements SET status=? WHERE id=?",
        (new_status, record_id)
    )
    conn.commit()
    conn.close()


def db_search(query: str) -> list:
    conn = get_conn()
    q = f"%{query.strip()}%"
    rows = conn.execute("""
        SELECT * FROM problem_statements
        WHERE id LIKE ? OR problem_statement LIKE ? OR business_objective LIKE ?
           OR solution_approach LIKE ? OR action_owner LIKE ?
           OR workflow_location LIKE ? OR business_value LIKE ?
        ORDER BY submitted_at DESC
    """, (q, q, q, q, q, q, q)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Module 2 — Feasibility assessments ────────────────────────────────────────

def db_save_assessment(rec: dict):
    conn = get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO feasibility_assessments
        (id, problem_id, assessed_at, assessor_name,
         ai_suitability_score, economic_viability_score, data_readiness_score,
         workflow_maturity_score, change_management_score,
         overall_score, verdict, ai_recommendation, responses)
        VALUES (:id, :problem_id, :assessed_at, :assessor_name,
                :ai_suitability_score, :economic_viability_score, :data_readiness_score,
                :workflow_maturity_score, :change_management_score,
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
