import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from src.database import get_connection

def render_analytics():
    st.markdown("## Support Analytics")

    conn = get_connection()
    df_tickets = pd.read_sql_query("SELECT * FROM tickets", conn)
    conn.close()

    if df_tickets.empty:
        st.info("No tickets to analyze. Ingest data first.")
        return

    # Visual Tabs mapping the requested sub-tabs
    tabs = st.tabs([
        "Volume", 
        "SLA", 
        "Categories", 
        "Sentiment", 
        "Churn Risk", 
        "Knowledge Gaps", 
        "Agent QA", 
        "Trends"
    ])

    with tabs[0]:
        st.markdown("### Ingestion Volume trends")
        df_tickets["date"] = pd.to_datetime(df_tickets["created_at"]).dt.date
        df_vol = df_tickets.groupby("date").size().reset_index(name="count")
        
        fig = px.line(df_vol, x="date", y="count", title="Daily Ticket Intake volume")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.markdown("### SLA Compliance")
        fig = px.pie(df_tickets, names="sla_risk", title="SLA Risk levels")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        st.markdown("### Category breakdown")
        fig = px.histogram(df_tickets, x="category", color="priority", title="Ticket count by Category")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[3]:
        st.markdown("### Sentiment Analysis")
        fig = px.histogram(df_tickets, x="sentiment", color="sentiment", title="Customer Sentiment distribution")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[4]:
        st.markdown("### Urgency vs Churn Risk mapping")
        fig = px.scatter(
            df_tickets, 
            x="urgency_score", 
            y="churn_risk", 
            color="sentiment",
            hover_name="ticket_id",
            size="resolution_confidence",
            title="Urgency vs Churn Risk Scatter"
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[5]:
        st.markdown("### Knowledge gaps log")
        conn = get_connection()
        df_gaps = pd.read_sql_query("SELECT * FROM knowledge_gaps", conn)
        conn.close()
        if not df_gaps.empty:
            st.dataframe(df_gaps[["category", "query_text", "affected_tickets_count", "recommendation"]], use_container_width=True, hide_index=True)
        else:
            st.success("No knowledge base gaps recorded.")

    with tabs[6]:
        st.markdown("### Agent Reply QA scores")
        fig = px.box(df_tickets, y="qa_score", points="all", title="QA Score spread")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[7]:
        st.markdown("### Root Cause Trend Clusters")
        conn = get_connection()
        df_trends = pd.read_sql_query("SELECT * FROM support_trends", conn)
        conn.close()
        if not df_trends.empty:
            st.dataframe(df_trends[["trend_name", "ticket_count", "severity", "product_area", "suggested_action"]], use_container_width=True, hide_index=True)
        else:
            st.info("No product trend clusters registered.")
