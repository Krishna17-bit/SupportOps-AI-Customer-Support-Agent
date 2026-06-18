from __future__ import annotations

import streamlit as st
from pathlib import Path

# Set up page configurations
st.set_page_config(
    page_title="SupportOps AI",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load white SaaS CSS theme
from src.ui_styles import APP_CSS
st.markdown(APP_CSS, unsafe_allow_html=True)

from src.llm import AIEngine
from src.views.dashboard import render_dashboard
from src.views.tickets import render_tickets
from src.views.sla_risk import render_sla_risk
from src.views.churn_risk import render_churn_risk
from src.views.knowledge_base import render_knowledge_base
from src.views.macros import render_macros
from src.views.reviews import render_reviews
from src.views.escalations import render_escalations
from src.views.customers import render_customers
from src.views.analytics import render_analytics
from src.views.knowledge_gaps import render_knowledge_gaps
from src.views.qa_review import render_qa_review
from src.views.automation_rules import render_automation_rules
from src.views.connectors import render_connectors
from src.views.evals import render_evals
from src.views.audit_logs import render_audit_logs
from src.views.settings import render_settings

# Initialize active engine
ai_engine = AIEngine()

# Render Sidebar Navigation
with st.sidebar:
    st.markdown('<div class="sidebar-header">◼ SupportOps AI</div>', unsafe_allow_html=True)
    st.markdown(
        "<span class='small-muted'>Customer support ticket triage, response grounding, SLA/churn mitigation, and QA operations panel.</span>",
        unsafe_allow_html=True
    )
    st.divider()

    # Route selection
    page = st.radio(
        "Navigation Menu",
        [
            "Dashboard",
            "Ticket Inbox",
            "SLA Risk Queue",
            "Churn Risk Detector",
            "Knowledge Base",
            "Macro Library",
            "Review Queue",
            "Escalations",
            "Customer 360",
            "Support Analytics",
            "Knowledge Gaps",
            "QA Review",
            "Automation Rules",
            "Connectors",
            "Evaluation Lab",
            "Runs & Audit Logs",
            "Settings"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("**LLM Engine Status**")
    if ai_engine.provider == "mock":
        st.info("Mock Demo Mode active")
    elif ai_engine.configured:
        st.success(f"Connected to {ai_engine.provider.upper()}")
    else:
        st.warning("Local rules mode active")
    st.caption(ai_engine.status_help)

# Route to corresponding render functions
if page == "Dashboard":
    render_dashboard()
elif page == "Ticket Inbox":
    render_tickets()
elif page == "SLA Risk Queue":
    render_sla_risk()
elif page == "Churn Risk Detector":
    render_churn_risk()
elif page == "Knowledge Base":
    render_knowledge_base()
elif page == "Macro Library":
    render_macros()
elif page == "Review Queue":
    render_reviews()
elif page == "Escalations":
    render_escalations()
elif page == "Customer 360":
    render_customers()
elif page == "Support Analytics":
    render_analytics()
elif page == "Knowledge Gaps":
    render_knowledge_gaps()
elif page == "QA Review":
    render_qa_review()
elif page == "Automation Rules":
    render_automation_rules()
elif page == "Connectors":
    render_connectors()
elif page == "Evaluation Lab":
    render_evals()
elif page == "Runs & Audit Logs":
    render_audit_logs()
elif page == "Settings":
    render_settings()
