import pytest
import sqlite3
import os
from src.database import get_connection, save_ticket, save_customer, log_audit, init_db

def test_database_init():
    # Make sure database initializes cleanly
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    assert "tickets" in tables
    assert "customers" in tables
    assert "audit_logs" in tables
    assert "provider_settings" in tables

def test_save_ticket():
    ticket = {
        "ticket_id": "T-TEST-99",
        "customer_name": "Test User",
        "email": "testuser@example.com",
        "subject": "Test ticket subject",
        "body": "Test ticket body text content.",
        "channel": "email",
        "status": "New",
        "priority": "Medium",
        "category": "General Support",
        "intent": "General Support Intent",
        "sentiment": "Neutral",
        "sla_due_time": "2026-06-19 12:00",
        "sla_risk": "Low SLA risk",
        "churn_risk": 10,
        "assigned_team": "Triage Pool",
        "assigned_agent": "",
        "created_at": "2026-06-18 12:00",
        "last_updated_at": "2026-06-18 12:00",
        "order_id": "",
        "latest_message": "Test ticket body text content.",
        "conversation_summary": "Test summary",
        "suggested_reply": "Hi Test User...",
        "linked_kb_article_id": "",
        "escalation_status": "None",
        "tags": "test",
        "internal_note": "Internal note test",
        "missing_info": "",
        "safety_flags": "",
        "qa_score": 90,
        "resolution_confidence": 80,
        "used_ai_refinement": 0
    }
    save_ticket(ticket)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = 'T-TEST-99'")
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row["customer_name"] == "Test User"
    assert row["subject"] == "Test ticket subject"

def test_log_audit():
    log_audit("Test Operation", "Input test log details", "Output test log details", "mock-provider", 120, "success")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row["operation"] == "Test Operation"
    assert row["provider_model"] == "mock-provider"
    assert row["latency_ms"] == 120
