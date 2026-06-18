import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
from src.database import get_connection

def render_dashboard():
    st.markdown("## Support Command Dashboard")
    st.markdown(
        '<div class="demo-banner"><span>💡 SupportOps AI is running in <b>Demo Mode</b>. You can view mock data or configure real LLM keys in Settings.</span></div>',
        unsafe_allow_html=True
    )

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch calculations from SQLite
    try:
        cursor.execute("SELECT COUNT(*) FROM tickets")
        total_tickets = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'New'")
        new_tickets = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Open'")
        open_tickets = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Resolved'")
        resolved_tickets = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tickets WHERE sla_risk = 'High SLA risk'")
        high_sla_risk = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM customers WHERE churn_risk >= 70")
        high_churn_cust = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tickets WHERE escalation_status = 'Escalated'")
        escalated_tickets = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tickets WHERE sentiment = 'Negative'")
        neg_sentiment = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(qa_score) FROM tickets WHERE qa_score IS NOT NULL")
        avg_qa = cursor.fetchone()[0] or 85.0

        cursor.execute("SELECT COUNT(*) FROM knowledge_articles")
        kb_articles = cursor.fetchone()[0]
    except Exception as e:
        st.error(f"Error fetching dashboard metrics: {e}")
        total_tickets = new_tickets = open_tickets = resolved_tickets = high_sla_risk = high_churn_cust = escalated_tickets = neg_sentiment = 0
        avg_qa = 85.0
        kb_articles = 0

    conn.close()

    # SLA Risk Banner Alert
    if high_sla_risk > 0:
        st.markdown(
            f'<div class="sla-warning-banner">⚠️ <b>Critical Warning:</b> There are currently {high_sla_risk} tickets at high risk of breaching SLA parameters. Review the SLA Risk Queue immediately.</div>',
            unsafe_allow_html=True
        )

    # Metric Row 1
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Total Tickets</div><div class="metric-value">{total_tickets}</div><div class="metric-note">Inbox ingestion count</div></div>',
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">New / Open</div><div class="metric-value">{new_tickets} / {open_tickets}</div><div class="metric-note">Unassigned triage queue</div></div>',
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">High SLA Risk</div><div class="metric-value" style="color: #ef4444 !important;">{high_sla_risk}</div><div class="metric-note">Action required under 4h</div></div>',
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">High Churn Risk</div><div class="metric-value" style="color: #f97316 !important;">{high_churn_cust}</div><div class="metric-note">VIP or angry accounts</div></div>',
            unsafe_allow_html=True
        )

    # Metric Row 2
    m5, m6, m7, m8 = st.columns(4)
    with m5:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Escalated</div><div class="metric-value" style="color: #3b82f6 !important;">{escalated_tickets}</div><div class="metric-note">Assigned to manager queue</div></div>',
            unsafe_allow_html=True
        )
    with m6:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Negative Sentiment</div><div class="metric-value">{neg_sentiment}</div><div class="metric-note">Angry customer replies</div></div>',
            unsafe_allow_html=True
        )
    with m7:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Avg QA Score</div><div class="metric-value">{avg_qa:.1f}%</div><div class="metric-note">Evidence-grounded responses</div></div>',
            unsafe_allow_html=True
        )
    with m8:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">KB Coverage</div><div class="metric-value">{kb_articles} articles</div><div class="metric-note">Active policy matches</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row
    c1, c2 = st.columns(2)
    conn = get_connection()
    df_tickets = pd.read_sql_query("SELECT category, sentiment, sla_risk FROM tickets", conn)
    conn.close()

    with c1:
        st.markdown("#### Volume by Category")
        if not df_tickets.empty:
            fig1 = px.histogram(df_tickets, y="category", color="sentiment", 
                                color_discrete_map={"Negative": "#fee2e2", "Neutral": "#cbd5e1", "Positive": "#d1fae5"},
                                orientation="h", height=320)
            fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                               font_color="#0f172a", margin=dict(l=0, r=0, t=20, b=0), yaxis_title="")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No ticket records available for categorization mapping.")

    with c2:
        st.markdown("#### SLA Risk Distribution")
        if not df_tickets.empty:
            fig2 = px.pie(df_tickets, names="sla_risk", color="sla_risk",
                          color_discrete_map={"High SLA risk": "#ef4444", "Medium SLA risk": "#f59e0b", "Low SLA risk": "#10b981"},
                          hole=0.4, height=320)
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#0f172a", margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No tickets to analyze for SLA distributions.")

    # Recent activity logs & Escalations
    st.divider()
    cl, cr = st.columns([2, 1])

    with cl:
        st.markdown("#### Recent Operations Audit Trail")
        conn = get_connection()
        df_logs = pd.read_sql_query("SELECT operation, input_summary, timestamp, status FROM audit_logs ORDER BY id DESC LIMIT 5", conn)
        conn.close()

        if not df_logs.empty:
            for _, log in df_logs.iterrows():
                time_str = log["timestamp"]
                # Clean ISO date format for visuals
                try:
                    time_str = datetime.fromisoformat(time_str).strftime("%b %d, %H:%M")
                except:
                    pass
                st.markdown(
                    f"""
                    <div class="timeline-item">
                        <div class="timeline-time">{time_str}</div>
                        <div class="timeline-content">
                            <b>{log['operation']}</b> · <span class="small-muted">{log['input_summary']}</span> 
                            <span class="status-pill {'pill-ok' if log['status']=='success' else 'pill-danger'}" style="float: right;">{log['status']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("Audit log is currently empty.")

    with cr:
        st.markdown("#### Escalated Incidents")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ticket_id, risk_type, severity FROM escalations WHERE status = 'Escalated' LIMIT 4")
        esc_items = cursor.fetchall()
        conn.close()

        if esc_items:
            for item in esc_items:
                st.markdown(
                    f"""
                    <div class="panel-compact">
                        <div style="font-weight: 600; font-size: 0.9rem;">Ticket ID: {item[0]}</div>
                        <div class="small-muted">Risk: {item[1]}</div>
                        <span class="status-pill pill-danger" style="margin-top: 4px;">{item[2]} Severity</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.success("No active escalated tickets needing emergency handling.")
