import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from src.database import get_connection, log_audit

def render_sla_risk():
    st.markdown("## SLA Risk Management")
    st.markdown("Monitor tickets approaching resolution deadlines or involving premium accounts.")

    conn = get_connection()
    df_sla = pd.read_sql_query("""
        SELECT ticket_id, customer_name, email, subject, priority, category, sla_risk, created_at, sla_due_time, status 
        FROM tickets 
        WHERE sla_risk IN ('High SLA risk', 'Medium SLA risk') OR status = 'New'
        ORDER BY urgency_score DESC
    """, conn)
    conn.close()

    if df_sla.empty:
        st.success("✅ Clean Slate! No tickets are currently at risk of breaching SLA parameters.")
        return

    # High risk highlight banner
    high_count = len(df_sla[df_sla["sla_risk"] == "High SLA risk"])
    if high_count > 0:
        st.markdown(
            f'<div class="sla-warning-banner">🚨 <b>Emergency Queue Alert:</b> {high_count} tickets are classified under High SLA risk. Action required immediately to avoid client agreement breach.</div>',
            unsafe_allow_html=True
        )

    # Search & filters
    st.markdown("### Active SLA Risk Queue")
    search_q = st.text_input("Search SLA Queue", "")
    if search_q:
        q = search_q.lower()
        df_sla = df_sla[
            df_sla["subject"].str.lower().str.contains(q) |
            df_sla["customer_name"].str.lower().str.contains(q) |
            df_sla["ticket_id"].str.lower().str.contains(q)
        ]

    # Show interactive queue table
    st.dataframe(
        df_sla[["ticket_id", "customer_name", "subject", "priority", "category", "sla_risk", "sla_due_time", "status"]],
        use_container_width=True,
        hide_index=True
    )

    # Batch Actions panel
    st.markdown("### Operations Actions")
    c1, c2 = st.columns(2)
    with c1:
        selected_ticket_id = st.selectbox("Select ticket ID to escalate:", df_sla["ticket_id"].tolist())
    with c2:
        escalate_action = st.button("Escalate to Tier-2 Queue", use_container_width=True)

    if escalate_action and selected_ticket_id:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check current ticket details
        cursor.execute("SELECT customer_name, email, category FROM tickets WHERE ticket_id = ?", (selected_ticket_id,))
        t_data = cursor.fetchone()
        
        if t_data:
            cust_name, email, category = t_data
            
            # Update ticket parameters
            cursor.execute("""
                UPDATE tickets 
                SET escalation_status = 'Escalated', assigned_team = 'Support Level 2', last_updated_at = ?
                WHERE ticket_id = ?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M"), selected_ticket_id))
            
            # Save into escalations table
            cursor.execute("""
                INSERT INTO escalations (ticket_id, risk_type, severity, time_remaining, customer_tier, reason, suggested_action, assigned_owner, status, created_at)
                VALUES (?, 'SLA Breach Threat', 'High', '2 hours', 'Enterprise', ?, 'Expedited developer ticket creation', 'Ops Manager', 'Escalated', ?)
            """, (selected_ticket_id, f"Escalated due to SLA Risk: {category}", datetime.now().isoformat()))
            
            conn.commit()
            log_audit("SLA Escalation", f"Ticket {selected_ticket_id} escalated manually", "Escalated to Support Level 2", "system", 0, "success")
            st.success(f"Ticket {selected_ticket_id} has been escalated to Tier-2 DevOps team.")
            st.rerun()
        conn.close()
