import sqlite3
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "supportops.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_reset=False):
    if force_reset and DB_PATH.exists():
        os.remove(DB_PATH)

    conn = get_connection()
    cursor = conn.cursor()

    # Create Tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        email TEXT PRIMARY KEY,
        name TEXT,
        company TEXT,
        tier TEXT,
        plan TEXT,
        arr_mrr TEXT,
        csat REAL,
        sla_policy TEXT,
        renewal_date TEXT,
        churn_risk INTEGER,
        tags TEXT,
        notes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id TEXT PRIMARY KEY,
        customer_name TEXT,
        email TEXT,
        subject TEXT,
        body TEXT,
        channel TEXT,
        status TEXT,
        priority TEXT,
        category TEXT,
        intent TEXT,
        sentiment TEXT,
        sla_due_time TEXT,
        sla_risk TEXT,
        churn_risk INTEGER,
        assigned_team TEXT,
        assigned_agent TEXT,
        created_at TEXT,
        last_updated_at TEXT,
        order_id TEXT,
        latest_message TEXT,
        conversation_summary TEXT,
        suggested_reply TEXT,
        linked_kb_article_id TEXT,
        escalation_status TEXT,
        tags TEXT,
        internal_note TEXT,
        missing_info TEXT,
        safety_flags TEXT,
        qa_score INTEGER,
        resolution_confidence INTEGER,
        used_ai_refinement INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ticket_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT,
        sender TEXT,
        message_text TEXT,
        created_at TEXT,
        FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_articles (
        article_id TEXT PRIMARY KEY,
        title TEXT,
        content TEXT,
        product_area TEXT,
        category TEXT,
        tags TEXT,
        status TEXT,
        last_updated TEXT,
        owner TEXT,
        usage_count INTEGER DEFAULT 0,
        helpfulness_score REAL DEFAULT 5.0,
        source TEXT,
        visibility TEXT,
        confidence_score REAL DEFAULT 1.0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS macros (
        macro_id TEXT PRIMARY KEY,
        title TEXT,
        category TEXT,
        content TEXT,
        approved_status TEXT,
        owner TEXT,
        last_reviewed TEXT,
        related_kb_articles TEXT,
        usage_count INTEGER DEFAULT 0,
        success_score REAL DEFAULT 5.0,
        risk_level TEXT,
        tags TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reply_drafts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT,
        draft_content TEXT,
        tone TEXT,
        confidence_score INTEGER,
        missing_knowledge_warning TEXT,
        risk_warnings TEXT,
        suggested_next_steps TEXT,
        internal_note TEXT,
        reviewer_status TEXT,
        approved_by TEXT,
        created_at TEXT,
        FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS review_decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_type TEXT,
        item_id TEXT,
        decision TEXT,
        comment TEXT,
        reviewer TEXT,
        timestamp TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS escalations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT,
        risk_type TEXT,
        severity TEXT,
        time_remaining TEXT,
        customer_tier TEXT,
        reason TEXT,
        suggested_action TEXT,
        assigned_owner TEXT,
        status TEXT,
        created_at TEXT,
        FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS support_trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trend_name TEXT,
        ticket_count INTEGER,
        example_tickets TEXT,
        severity TEXT,
        product_area TEXT,
        suggested_action TEXT,
        suggested_kb_article TEXT,
        suggested_macro TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_gaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT,
        category TEXT,
        affected_tickets_count INTEGER,
        recommendation TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS qa_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT,
        qa_score INTEGER,
        accuracy_score INTEGER,
        empathy_score INTEGER,
        completeness_score INTEGER,
        policy_compliance TEXT,
        issues_detected TEXT,
        suggested_rewrite TEXT,
        status TEXT,
        reviewer TEXT,
        created_at TEXT,
        FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS automation_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_name TEXT,
        condition_type TEXT,
        condition_value TEXT,
        action_type TEXT,
        action_value TEXT,
        is_enabled INTEGER DEFAULT 1,
        risk_level TEXT,
        owner TEXT,
        last_triggered TEXT,
        trigger_count INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS connectors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        status TEXT,
        auth_method TEXT,
        last_sync TEXT,
        sync_errors TEXT,
        data_scope TEXT,
        connected_workflows TEXT,
        risk_level TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS run_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation TEXT,
        input_summary TEXT,
        output_summary TEXT,
        provider_model TEXT,
        latency_ms INTEGER,
        token_cost REAL,
        status TEXT,
        error_message TEXT,
        timestamp TEXT,
        user_reviewer TEXT,
        related_ticket_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation TEXT,
        input_summary TEXT,
        output_summary TEXT,
        provider_model TEXT,
        latency_ms INTEGER,
        token_cost REAL,
        status TEXT,
        error_message TEXT,
        timestamp TEXT,
        user_reviewer TEXT,
        related_ticket_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eval_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_name TEXT,
        provider_model TEXT,
        input_tokens INTEGER,
        output_tokens INTEGER,
        status TEXT,
        accuracy REAL,
        findings TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS provider_settings (
        provider_name TEXT PRIMARY KEY,
        is_active INTEGER,
        api_key TEXT,
        model_name TEXT,
        base_url TEXT
    )
    """)

    conn.commit()
    conn.close()

# Helper Functions for DB Interactions
def load_all_tickets() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM tickets", conn)
    conn.close()
    return df

def save_ticket(ticket_dict: dict):
    conn = get_connection()
    cursor = conn.cursor()
    fields = list(ticket_dict.keys())
    placeholders = ", ".join(["?"] * len(fields))
    columns = ", ".join(fields)
    update_str = ", ".join([f"{k} = ?" for k in fields])
    
    # Try insert or update
    try:
        cursor.execute(f"INSERT INTO tickets ({columns}) VALUES ({placeholders})", list(ticket_dict.values()))
    except sqlite3.IntegrityError:
        cursor.execute(f"UPDATE tickets SET {update_str} WHERE ticket_id = ?", list(ticket_dict.values()) + [ticket_dict["ticket_id"]])
    conn.commit()
    conn.close()

def save_customer(cust_dict: dict):
    conn = get_connection()
    cursor = conn.cursor()
    fields = list(cust_dict.keys())
    placeholders = ", ".join(["?"] * len(fields))
    columns = ", ".join(fields)
    update_str = ", ".join([f"{k} = ?" for k in fields])
    try:
        cursor.execute(f"INSERT INTO customers ({columns}) VALUES ({placeholders})", list(cust_dict.values()))
    except sqlite3.IntegrityError:
        cursor.execute(f"UPDATE customers SET {update_str} WHERE email = ?", list(cust_dict.values()) + [cust_dict["email"]])
    conn.commit()
    conn.close()

def save_article(art_dict: dict):
    conn = get_connection()
    cursor = conn.cursor()
    fields = list(art_dict.keys())
    placeholders = ", ".join(["?"] * len(fields))
    columns = ", ".join(fields)
    update_str = ", ".join([f"{k} = ?" for k in fields])
    try:
        cursor.execute(f"INSERT INTO knowledge_articles ({columns}) VALUES ({placeholders})", list(art_dict.values()))
    except sqlite3.IntegrityError:
        cursor.execute(f"UPDATE knowledge_articles SET {update_str} WHERE article_id = ?", list(art_dict.values()) + [art_dict["article_id"]])
    conn.commit()
    conn.close()

def save_macro(macro_dict: dict):
    conn = get_connection()
    cursor = conn.cursor()
    fields = list(macro_dict.keys())
    placeholders = ", ".join(["?"] * len(fields))
    columns = ", ".join(fields)
    update_str = ", ".join([f"{k} = ?" for k in fields])
    try:
        cursor.execute(f"INSERT INTO macros ({columns}) VALUES ({placeholders})", list(macro_dict.values()))
    except sqlite3.IntegrityError:
        cursor.execute(f"UPDATE macros SET {update_str} WHERE macro_id = ?", list(macro_dict.values()) + [macro_dict["macro_id"]])
    conn.commit()
    conn.close()

def log_audit(operation, input_summary, output_summary, provider_model="mock", latency_ms=0, status="success", error_message="", user_reviewer="", related_ticket_id=""):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute("""
    INSERT INTO audit_logs (operation, input_summary, output_summary, provider_model, latency_ms, status, error_message, timestamp, user_reviewer, related_ticket_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (operation, input_summary, output_summary, provider_model, latency_ms, status, error_message, timestamp, user_reviewer, related_ticket_id))
    
    # Also log to runs database
    cursor.execute("""
    INSERT INTO run_logs (operation, input_summary, output_summary, provider_model, latency_ms, status, error_message, timestamp, user_reviewer, related_ticket_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (operation, input_summary, output_summary, provider_model, latency_ms, status, error_message, timestamp, user_reviewer, related_ticket_id))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
