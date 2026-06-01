from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis_engine import analyze_tickets, detect_kb_gaps, macro_recommendations
from src.data_loader import load_knowledge_uploads, load_order_history, load_sample_knowledge, load_tickets
from src.exporter import write_exports
from src.llm import AIEngine
from src.ui_styles import APP_CSS

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="SupportOps AI",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(APP_CSS, unsafe_allow_html=True)


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill(text: str, kind: str = "") -> str:
    css = "status-pill"
    if kind == "danger":
        css += " pill-danger"
    elif kind == "warn":
        css += " pill-warn"
    elif kind == "ok":
        css += " pill-ok"
    return f"<span class='{css}'>{text}</span>"


ai_engine = AIEngine()

with st.sidebar:
    st.markdown("### SupportOps AI")
    st.markdown(
        "Support intelligence workspace for ticket triage, evidence-grounded replies, refund review, SLA risk, churn risk, and QA-safe support operations."
    )
    st.divider()
    st.markdown("**Connection status**")
    if ai_engine.configured:
        st.success("AI analysis engine configured")
    else:
        st.warning("Local rules mode")
    st.caption(ai_engine.status_help)
    st.divider()
    max_tickets = st.slider("Tickets to process", 5, 250, 50, step=5)
    ai_refine_limit = st.slider("AI refinement limit", 0, 100, 25, step=5)
    st.caption("Use a smaller AI limit for faster testing. Rules still process all selected tickets.")
    st.divider()
    st.markdown("**Advanced checks included**")
    st.markdown(
        "- Bulk triage\n"
        "- Evidence-grounded reply drafting\n"
        "- Refund eligibility review\n"
        "- SLA breach risk\n"
        "- Churn-risk scoring\n"
        "- Escalation detection\n"
        "- Prompt-injection and PII flags\n"
        "- Support QA scoring\n"
        "- KB gap detection\n"
        "- CSV + audit JSON export"
    )

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">SupportOps AI</div>
        <div class="hero-subtitle">
            Customer support ticket triage and resolution workspace for small teams that need fast, source-grounded support operations without migrating into a heavy helpdesk platform.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### 1. Upload support tickets and knowledge base files")

c1, c2 = st.columns([1, 1])
with c1:
    ticket_file = st.file_uploader(
        "Upload tickets CSV/XLSX/JSON/TXT",
        type=["csv", "xlsx", "xls", "json", "txt"],
        help="Expected columns can include ticket_id, customer_name, email, subject, body, channel, created_at, order_id. Missing columns are filled safely.",
    )
with c2:
    kb_files = st.file_uploader(
        "Upload policies, FAQs, docs, CSVs, PDFs, DOCX",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "md", "csv", "xlsx", "json"],
        help="Add refund policy, SLA policy, FAQ, product docs, order exports, or internal support guidelines.",
    )

use_sample_knowledge = st.checkbox("Include sample support knowledge base", value=True)
run = st.button("Run support analysis", use_container_width=True)

if "results_df" not in st.session_state:
    st.session_state.results_df = None
if "audit" not in st.session_state:
    st.session_state.audit = []
if "tickets_df" not in st.session_state:
    st.session_state.tickets_df = None

if run:
    with st.spinner("Analyzing tickets, retrieving policy evidence, and drafting support responses..."):
        tickets_df = load_tickets(ticket_file, BASE_DIR)
        docs = []
        if use_sample_knowledge:
            docs.extend(load_sample_knowledge(BASE_DIR))
        docs.extend(load_knowledge_uploads(kb_files))
        order_history = load_order_history(BASE_DIR)
        results_df, audit = analyze_tickets(
            tickets_df=tickets_df,
            docs=docs,
            order_history=order_history,
            ai_engine=ai_engine,
            max_tickets=max_tickets,
            ai_refine_limit=ai_refine_limit,
        )
        st.session_state.results_df = results_df
        st.session_state.audit = audit
        st.session_state.tickets_df = tickets_df
        st.session_state.docs_count = len(docs)

results_df = st.session_state.results_df

if results_df is None:
    st.markdown(
        """
        <div class="panel">
            <b>How to test quickly</b><br>
            <span class="small-muted">
            Do not upload anything first. Keep “Include sample support knowledge base” checked and click Run support analysis. The app will use sample tickets, refund policy, FAQ, SLA policy, order history, and support guidelines.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

st.divider()
st.markdown("## Workflow result")

high_urgency = int((results_df["urgency_score"] >= 75).sum())
escalations = int(results_df["escalation_required"].sum())
weak_evidence = int(results_df["evidence_strength"].isin(["Weak", "No evidence found"]).sum())
avg_conf = int(results_df["resolution_confidence"].mean()) if not results_df.empty else 0

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Tickets analyzed", str(len(results_df)), "Bulk CSV/XLSX-ready workflow")
with m2:
    metric_card("Escalations", str(escalations), "Needs human review before reply")
with m3:
    metric_card("Weak evidence", str(weak_evidence), "Potential KB/policy gap")
with m4:
    metric_card("Avg confidence", f"{avg_conf}%", "Grounded resolution confidence")

tabs = st.tabs(
    [
        "Ticket Triage",
        "Reply Assistant",
        "Evidence Map",
        "Refund & Escalation",
        "SLA + Churn Risk",
        "Support Analytics",
        "KB Gaps + Macros",
        "Audit + Export",
    ]
)

with tabs[0]:
    st.markdown("### Ticket triage table")
    visible_cols = [
        "ticket_id", "customer_name", "subject", "category", "urgency_score", "sentiment", "churn_risk", "sla_risk",
        "escalation_required", "refund_decision", "evidence_strength", "qa_score", "resolution_confidence", "used_ai_refinement"
    ]
    st.dataframe(results_df[visible_cols], use_container_width=True, hide_index=True)

with tabs[1]:
    st.markdown("### Evidence-grounded reply drafts")
    selected_ticket = st.selectbox("Select ticket", results_df["ticket_id"].tolist())
    row = results_df[results_df["ticket_id"] == selected_ticket].iloc[0]
    st.markdown(
        f"""
        <div class="panel">
            <b>{row['subject']}</b><br>
            {pill(row['category'])} {pill(row['sentiment'], 'danger' if row['sentiment'] == 'Negative' else '')} {pill(row['evidence_strength'], 'ok' if row['evidence_strength'] == 'Strong' else 'warn')}
            <br><br><span class="small-muted">Original ticket</span><br>{row['body']}
        </div>
        """,
        unsafe_allow_html=True,
    )
    edited_reply = st.text_area("Draft reply for human review", value=row["suggested_reply"], height=260)
    st.caption("This app prepares replies for review. It does not auto-send customer emails.")
    st.markdown("#### Internal review note")
    st.write(row["internal_note"])
    if row["missing_info"]:
        st.warning(f"Missing information: {row['missing_info']}")
    if row["safety_flags"]:
        st.error(f"Safety flags: {row['safety_flags']}")
    st.download_button(
        "Download this reply as TXT",
        data=edited_reply,
        file_name=f"{selected_ticket}_reply.txt",
        mime="text/plain",
        use_container_width=True,
    )

with tabs[2]:
    st.markdown("### Evidence map")
    for _, row in results_df.iterrows():
        with st.expander(f"{row['ticket_id']} · {row['category']} · {row['evidence_strength']}"):
            st.write(row["subject"])
            evidence = row.get("evidence", [])
            if evidence:
                for ev in evidence:
                    st.markdown(
                        f"""
                        <div class="evidence">
                            <b>{ev['source_title']} · score {ev['score']}</b><br>
                            <span>{ev['quote'][:1200]}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.warning("No supporting evidence found. Human review needed before sending a reply.")

with tabs[3]:
    st.markdown("### Refund and escalation review")
    review_cols = ["ticket_id", "customer_name", "category", "order_id", "refund_decision", "escalation_required", "missing_info", "safety_flags"]
    st.dataframe(results_df[review_cols], use_container_width=True, hide_index=True)
    st.markdown(
        """
        <div class="panel">
            <b>Guardrail</b><br>
            <span class="small-muted">The agent never approves money movement by itself. Refunds, credits, cancellations, legal complaints, payment-data mentions, and unsafe instructions are routed to human review.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tabs[4]:
    st.markdown("### SLA and churn risk")
    risk_df = results_df[["ticket_id", "subject", "urgency_score", "churn_risk", "sla_risk", "sentiment", "escalation_required"]]
    st.dataframe(risk_df.sort_values(["churn_risk", "urgency_score"], ascending=False), use_container_width=True, hide_index=True)
    fig = px.scatter(
        results_df,
        x="urgency_score",
        y="churn_risk",
        hover_name="ticket_id",
        hover_data=["category", "sentiment", "sla_risk"],
        size="resolution_confidence",
        title="Urgency vs Churn Risk",
    )
    fig.update_layout(height=420, paper_bgcolor="#111111", plot_bgcolor="#111111", font_color="#ffffff")
    st.plotly_chart(fig, use_container_width=True)

with tabs[5]:
    st.markdown("### Support analytics")
    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.histogram(results_df, x="category", title="Ticket categories")
        fig1.update_layout(height=380, paper_bgcolor="#111111", plot_bgcolor="#111111", font_color="#ffffff", xaxis_title="")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.histogram(results_df, x="evidence_strength", title="Evidence coverage")
        fig2.update_layout(height=380, paper_bgcolor="#111111", plot_bgcolor="#111111", font_color="#ffffff", xaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### Top risky tickets")
        st.dataframe(
            results_df.sort_values(["churn_risk", "urgency_score"], ascending=False)[["ticket_id", "subject", "churn_risk", "urgency_score", "sla_risk"]].head(10),
            use_container_width=True,
            hide_index=True,
        )
    with c4:
        st.markdown("#### Quality distribution")
        st.dataframe(
            results_df[["ticket_id", "qa_score", "resolution_confidence", "evidence_strength"]].sort_values("qa_score"),
            use_container_width=True,
            hide_index=True,
        )

with tabs[6]:
    st.markdown("### Knowledge base gaps")
    gaps = detect_kb_gaps(results_df)
    st.dataframe(gaps, use_container_width=True, hide_index=True)
    st.markdown("### Suggested macros")
    macros = macro_recommendations(results_df)
    st.dataframe(macros, use_container_width=True, hide_index=True)
    st.download_button(
        "Download macro suggestions CSV",
        data=macros.to_csv(index=False),
        file_name="supportops_macro_suggestions.csv",
        mime="text/csv",
        use_container_width=True,
    )

with tabs[7]:
    st.markdown("### Audit package")
    st.code(json.dumps(st.session_state.audit[:8], indent=2, ensure_ascii=False), language="json")
    paths = write_exports(BASE_DIR, results_df, st.session_state.audit)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Download triaged tickets CSV",
            data=paths["csv"].read_bytes(),
            file_name=paths["csv"].name,
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "Download audit JSON",
            data=paths["json"].read_bytes(),
            file_name=paths["json"].name,
            mime="application/json",
            use_container_width=True,
        )
