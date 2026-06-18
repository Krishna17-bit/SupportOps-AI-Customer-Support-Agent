import pytest
import pandas as pd
from src.rules import classify_category, sentiment_label, urgency_score, sla_risk, churn_risk, qa_score
from src.retrieval import tokenize, retrieve_evidence, evidence_strength, KnowledgeDoc

def test_classify_category():
    assert classify_category("Refund request for damaged item") == "Refund / Return"
    assert classify_category("My login is locked, help me reset password") == "Account / Access"
    assert classify_category("Workspace is down for all users production block") == "Outage / Incident"
    assert classify_category("Just a general support query about setting limits") == "Product Question"

def test_sentiment_label():
    label, score = sentiment_label("I am furious and disappointed with this terrible service!")
    assert label == "Negative"
    assert score >= 65

    label, score = sentiment_label("Thank you so much! Great support!")
    assert label == "Positive"
    assert score == 25

def test_urgency_score():
    assert urgency_score("critical system outage, production is down ASAP!", "Outage / Incident") >= 70
    assert urgency_score("just a question", "General Support") <= 40

def test_sla_risk():
    # Test high SLA risk with high urgency
    row = {"created_at": "2026-06-18 10:00:00"}
    assert sla_risk(row, 85) == "High SLA risk"
    
    # Test old ticket
    row = {"created_at": "2026-05-18 10:00:00"}
    assert sla_risk(row, 40) == "High SLA risk"

def test_churn_risk():
    assert churn_risk("cancel plan immediately and move to competitor", 80, 75) >= 70
    assert churn_risk("nice product", 20, 20) <= 30

def test_qa_score():
    # Test reply with good content and grounding
    assert qa_score("Hi there, sorry about that. Let me look at order SO-123. Thanks.", 1, False) >= 70

def test_tokenize():
    tokens = tokenize("The quick brown fox jumps over the lazy dog.")
    assert "quick" in tokens
    assert "the" not in tokens

def test_retrieve_evidence():
    docs = [
        KnowledgeDoc("Refund Policy", "Refunds are eligible within 30 days of purchase for damaged items.", "md"),
        KnowledgeDoc("Login Guide", "To enable 2FA, navigate to dashboard security tab.", "md")
    ]
    hits = retrieve_evidence("refund request for damaged product", docs)
    assert len(hits) > 0
    assert hits[0].source_title == "Refund Policy"
    assert evidence_strength(hits) == "Strong"
