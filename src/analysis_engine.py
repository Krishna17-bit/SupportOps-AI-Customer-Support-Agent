from __future__ import annotations

import re
from typing import Dict, List, Tuple

import pandas as pd

from .data_loader import KnowledgeDoc
from .llm import AIEngine
from .retrieval import evidence_strength, retrieve_evidence
from .rules import (
    churn_risk,
    classify_category,
    detect_safety_flags,
    qa_score,
    refund_decision,
    sentiment_label,
    sla_risk,
    urgency_score,
)


def _safe_str(value) -> str:
    if value is None:
        return ""
    return str(value)


def _reply_template(row: Dict, category: str, evidence: List[Dict], refund: str, missing: List[str]) -> str:
    name = _safe_str(row.get("customer_name")) or "there"
    evidence_line = ""
    if evidence:
        evidence_line = f" Based on our current policy information, {evidence[0]['quote'][:180].strip()}..."
    ask = ""
    if missing:
        ask = " Could you please share " + ", ".join(missing[:3]) + " so we can check this accurately?"

    if category == "Refund / Return":
        return (
            f"Hi {name}, thanks for reaching out. I understand you want help with a refund or return. "
            f"{evidence_line} Our current review status is: {refund}." + ask +
            " Once we have the missing details, we can confirm the next step without making assumptions."
        )
    if category == "Bug / Technical Issue":
        return (
            f"Hi {name}, thanks for reporting this. I’m sorry for the disruption. "
            f"{evidence_line} I’ll share this with the support team for technical review. "
            "Please send any screenshots, error messages, browser/device details, and the exact steps that caused the issue."
        )
    if category == "Billing":
        return (
            f"Hi {name}, thanks for contacting us about billing. {evidence_line} "
            "To verify this safely, please share the invoice number or order ID, but do not send full card details."
        )
    return (
        f"Hi {name}, thanks for reaching out. {evidence_line} "
        "I’ve noted your request and will help route it to the right next step. "
        "Please share any missing context that may help us resolve this faster."
    )


def _missing_info(row: Dict, category: str) -> List[str]:
    missing = []
    if not _safe_str(row.get("email")):
        missing.append("customer email")
    if category in {"Refund / Return", "Delivery / Order Status", "Billing"} and not _safe_str(row.get("order_id")):
        missing.append("order ID")
    if category == "Bug / Technical Issue":
        body = _safe_str(row.get("body")).lower()
        if "screenshot" not in body and "error" not in body:
            missing.append("screenshot or exact error message")
        if "browser" not in body and "device" not in body:
            missing.append("browser/device details")
    return missing


def analyze_tickets(
    tickets_df: pd.DataFrame,
    docs: List[KnowledgeDoc],
    order_history: pd.DataFrame,
    ai_engine: AIEngine,
    max_tickets: int = 100,
    ai_refine_limit: int = 25,
) -> Tuple[pd.DataFrame, List[Dict]]:
    working = tickets_df.head(max_tickets).copy()
    rows: List[Dict] = []
    ai_items: List[Dict] = []

    for _, row in working.iterrows():
        raw = row.to_dict()
        text = _safe_str(raw.get("full_text")) or f"{raw.get('subject', '')}\n{raw.get('body', '')}"
        category = classify_category(text)
        sentiment, sentiment_score = sentiment_label(text)
        urgency = urgency_score(text, category)
        churn = churn_risk(text, sentiment_score, urgency)
        safety_flags = detect_safety_flags(text)
        missing = _missing_info(raw, category)
        refund = refund_decision(raw, category, order_history)
        evidence_hits = retrieve_evidence(text + " " + category, docs, top_k=4)
        evidence = [
            {"source_title": hit.source_title, "quote": hit.quote, "score": hit.score}
            for hit in evidence_hits
        ]
        escalation = (
            urgency >= 75
            or churn >= 70
            or bool(safety_flags)
            or category == "Complaint / Escalation"
            or "Needs review" in refund
        )
        reply = _reply_template(raw, category, evidence, refund, missing)
        qa = qa_score(reply, len(evidence), escalation)
        confidence = int(min(98, max(20, (evidence_hits[0].score * 100 if evidence_hits else 25) + qa * 0.35)))

        result = {
            "ticket_id": _safe_str(raw.get("ticket_id")),
            "customer_name": _safe_str(raw.get("customer_name")),
            "email": _safe_str(raw.get("email")),
            "subject": _safe_str(raw.get("subject")),
            "body": _safe_str(raw.get("body")),
            "channel": _safe_str(raw.get("channel")),
            "created_at": _safe_str(raw.get("created_at")),
            "order_id": _safe_str(raw.get("order_id")),
            "category": category,
            "urgency_score": urgency,
            "sentiment": sentiment,
            "churn_risk": churn,
            "sla_risk": sla_risk(raw, urgency),
            "escalation_required": escalation,
            "refund_decision": refund,
            "evidence_strength": evidence_strength(evidence_hits),
            "evidence_count": len(evidence),
            "top_evidence_source": evidence[0]["source_title"] if evidence else "",
            "top_evidence_quote": evidence[0]["quote"][:480] if evidence else "",
            "suggested_reply": reply,
            "internal_note": "Review before sending. Do not promise refunds, credits, bug fixes, or delivery timelines unless verified.",
            "missing_info": "; ".join(missing),
            "safety_flags": "; ".join(safety_flags),
            "qa_score": qa,
            "resolution_confidence": confidence,
            "evidence": evidence,
            "used_ai_refinement": False,
        }
        rows.append(result)
        if len(ai_items) < ai_refine_limit:
            ai_items.append(
                {
                    "ticket_id": result["ticket_id"],
                    "subject": result["subject"],
                    "body": result["body"],
                    "heuristics": {k: result[k] for k in ["category", "urgency_score", "sentiment", "churn_risk", "refund_decision", "missing_info", "safety_flags"]},
                    "evidence": evidence,
                }
            )

    refinements = ai_engine.refine_batch(ai_items)
    for item in rows:
        refined = refinements.get(item["ticket_id"])
        if not refined:
            continue
        item["category"] = refined.get("category") or item["category"]
        item["urgency_score"] = int(refined.get("urgency_score") or item["urgency_score"])
        item["sentiment"] = refined.get("sentiment") or item["sentiment"]
        item["churn_risk"] = int(refined.get("churn_risk") or item["churn_risk"])
        item["escalation_required"] = bool(refined.get("escalation_required", item["escalation_required"]))
        item["refund_decision"] = refined.get("refund_decision") or item["refund_decision"]
        item["suggested_reply"] = refined.get("suggested_reply") or item["suggested_reply"]
        item["internal_note"] = refined.get("internal_note") or item["internal_note"]
        item["missing_info"] = "; ".join(refined.get("missing_info", [])) if isinstance(refined.get("missing_info"), list) else item["missing_info"]
        item["safety_flags"] = "; ".join(refined.get("safety_flags", [])) if isinstance(refined.get("safety_flags"), list) else item["safety_flags"]
        item["qa_score"] = int(refined.get("qa_score") or item["qa_score"])
        item["sla_risk"] = sla_risk(item, item["urgency_score"])
        item["used_ai_refinement"] = True

    output_df = pd.DataFrame(rows)
    audit = []
    for item in rows:
        audit.append(
            {
                "ticket_id": item["ticket_id"],
                "decision_summary": {
                    "category": item["category"],
                    "urgency_score": item["urgency_score"],
                    "sentiment": item["sentiment"],
                    "churn_risk": item["churn_risk"],
                    "escalation_required": item["escalation_required"],
                    "refund_decision": item["refund_decision"],
                    "evidence_strength": item["evidence_strength"],
                    "used_ai_refinement": item["used_ai_refinement"],
                },
                "evidence": item["evidence"],
                "reply": item["suggested_reply"],
            }
        )
    return output_df, audit


def detect_kb_gaps(results_df: pd.DataFrame) -> pd.DataFrame:
    if results_df.empty:
        return pd.DataFrame(columns=["gap", "affected_tickets", "recommendation"])
    weak = results_df[results_df["evidence_strength"].isin(["Weak", "No evidence found"])]
    rows = []
    for category, group in weak.groupby("category"):
        rows.append(
            {
                "gap": f"Weak or missing knowledge base coverage for {category}",
                "affected_tickets": len(group),
                "recommendation": f"Create a verified help article or internal macro for {category} with approved steps, policy boundaries, and escalation rules.",
            }
        )
    return pd.DataFrame(rows).sort_values("affected_tickets", ascending=False) if rows else pd.DataFrame(columns=["gap", "affected_tickets", "recommendation"])


def macro_recommendations(results_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if results_df.empty:
        return pd.DataFrame(columns=["macro_name", "trigger", "draft"])
    for category, group in results_df.groupby("category"):
        if len(group) < 1:
            continue
        top_missing = "; ".join([x for x in group["missing_info"].dropna().astype(str).head(3) if x])
        rows.append(
            {
                "macro_name": f"{category} first response",
                "trigger": f"Use when ticket category is {category} and evidence strength is moderate/strong.",
                "draft": f"Thank the customer, acknowledge the issue, reference the approved policy/doc, ask for missing info if needed ({top_missing or 'none'}), and avoid promising unverified outcomes.",
            }
        )
    return pd.DataFrame(rows)
