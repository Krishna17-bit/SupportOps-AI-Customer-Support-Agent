from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd


CATEGORY_KEYWORDS = {
    "Outage / Incident": ["outage", "workspace is down", "down for all", "production", "critical", "all users", "service down"],
    "Subscription / Cancellation": ["cancel subscription", "subscription cancellation", "cancel my plan", "move to a competitor", "competitor"],
    "Refund / Return": ["refund", "return", "exchange", "money back", "chargeback"],
    "Billing": ["invoice", "billing", "charged", "payment", "card", "subscription", "receipt", "tax"],
    "Bug / Technical Issue": ["bug", "error", "crash", "not working", "broken", "login", "failed", "timeout", "issue"],
    "Delivery / Order Status": ["delivery", "delivered", "shipping", "tracking", "order status", "late", "courier"],
    "Product Question": ["how to", "feature", "support", "compatible", "setup", "install", "configuration"],
    "Account / Access": ["password", "access", "locked", "account", "2fa", "login", "permission"],
    "Complaint / Escalation": ["angry", "terrible", "unacceptable", "manager", "legal", "lawsuit", "complaint", "escalate"],
}

NEGATIVE = ["angry", "furious", "terrible", "unacceptable", "bad", "worst", "disappointed", "frustrated", "legal", "chargeback", "cancel"]
POSITIVE = ["thanks", "thank you", "great", "helpful", "appreciate", "love"]
URGENT = ["urgent", "asap", "immediately", "today", "critical", "blocked", "production", "down", "breach", "legal", "chargeback"]
PROMPT_INJECTION = ["ignore previous", "system prompt", "developer message", "reveal", "api key", "password", "secret", "bypass", "jailbreak"]
PII_PATTERNS = {
    "possible_phone": re.compile(r"(?:\+?\d[\s-]?){8,}"),
    "possible_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
}


def text_blob(row: Dict) -> str:
    return f"{row.get('subject', '')}\n{row.get('body', '')}".lower()


def classify_category(text: str) -> str:
    text_l = text.lower()
    scores = {}
    for cat, terms in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for term in terms if term in text_l)
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "General Support"
    return best


def sentiment_label(text: str) -> Tuple[str, int]:
    text_l = text.lower()
    neg = sum(1 for w in NEGATIVE if w in text_l)
    pos = sum(1 for w in POSITIVE if w in text_l)
    if neg >= 2 or (neg >= 1 and "!" in text):
        return "Negative", max(65, min(95, 55 + neg * 12))
    if pos > neg:
        return "Positive", 25
    return "Neutral", 45


def urgency_score(text: str, category: str) -> int:
    text_l = text.lower()
    score = 25
    score += 14 * sum(1 for w in URGENT if w in text_l)
    if category in {"Complaint / Escalation", "Bug / Technical Issue", "Outage / Incident"}:
        score += 18
    if "enterprise" in text_l or "paid plan" in text_l:
        score += 8
    return max(0, min(100, score))


def detect_safety_flags(text: str) -> List[str]:
    text_l = text.lower()
    flags: List[str] = []
    for term in PROMPT_INJECTION:
        if term in text_l:
            flags.append("Prompt-injection / unsafe instruction attempt")
            break
    for label, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            flags.append(label.replace("_", " "))
    if "credit card" in text_l or "card number" in text_l:
        flags.append("Payment data mentioned")
    return sorted(set(flags))


def refund_decision(row: Dict, category: str, order_history: pd.DataFrame) -> str:
    if category != "Refund / Return":
        return "Not a refund ticket"
    order_id = str(row.get("order_id", "")).strip()
    if not order_id:
        return "Needs review: order ID missing"

    if order_history is None or order_history.empty or "order_id" not in order_history.columns:
        return "Needs review: no order history available"

    match = order_history[order_history["order_id"].astype(str).str.lower() == order_id.lower()]
    if match.empty:
        return "Needs review: order not found"

    order = match.iloc[0].to_dict()
    status = str(order.get("status", "")).lower()
    if "delivered" not in status and "completed" not in status:
        return "Needs review: order not marked delivered/completed"

    return "Potentially eligible: verify return window and condition"


def sla_risk(row: Dict, urgency: int) -> str:
    created = row.get("created_at", "")
    try:
        created_dt = pd.to_datetime(created)
        age_hours = (pd.Timestamp.now() - created_dt).total_seconds() / 3600
    except Exception:
        age_hours = 0

    if urgency >= 80 or age_hours > 24:
        return "High SLA risk"
    if urgency >= 55 or age_hours > 12:
        return "Medium SLA risk"
    return "Low SLA risk"


def churn_risk(text: str, sentiment_score: int, urgency: int) -> int:
    text_l = text.lower()
    score = 0
    score += sentiment_score * 0.45
    score += urgency * 0.35
    if "cancel" in text_l or "competitor" in text_l or "switch" in text_l:
        score += 22
    if "legal" in text_l or "chargeback" in text_l:
        score += 20
    return int(max(0, min(100, score)))


def qa_score(reply: str, evidence_count: int, escalation: bool) -> int:
    score = 55
    if len(reply) > 250:
        score += 10
    if any(w in reply.lower() for w in ["sorry", "understand", "thanks", "thank you"]):
        score += 10
    if evidence_count:
        score += 15
    if escalation:
        score += 5
    return max(0, min(100, score))
