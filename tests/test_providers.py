import pytest
from src.llm import AIEngine

def test_mock_provider_fallback():
    engine = AIEngine()
    # Mock should be configured automatically
    assert engine.provider in ["mock", "gemini"] or engine.configured
    
    # Batch refinement under mock mode should return valid outputs
    items = [{
        "ticket_id": "T-EVAL-01",
        "subject": "damaged items refund",
        "body": "The glass table arrived broken yesterday. Need refund.",
        "heuristics": {"category": "Refund / Return", "urgency_score": 80, "sentiment": "Negative", "churn_risk": 50, "refund_decision": "Potentially eligible"},
        "evidence": [{"source_title": "Refund Policy", "quote": "Refunds eligible within 30 days for broken goods.", "score": 0.9}]
    }]
    
    results = engine.refine_batch(items)
    assert "T-EVAL-01" in results
    res = results["T-EVAL-01"]
    assert res["category"] == "Refund / Return"
    assert "refund" in res["suggested_reply"].lower()
    assert res["qa_score"] > 50

def test_connection_testing():
    engine = AIEngine()
    
    # Mock connection test should succeed immediately
    res = engine.test_connection("mock", "", "mock-model")
    assert res.ok
    assert "succeeded" in res.message.lower()
    
    # Missing key connection test should fail
    res = engine.test_connection("openai", "", "gpt-4o-mini")
    assert not res.ok
    assert "required" in res.message.lower()
