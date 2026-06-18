import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from src.database import get_connection, log_audit

def render_escalations():
    st.markdown("## Escalations Dashboard")
    st.markdown("Track and resolve high-risk support items assigned to support team supervisors, customer success leads, or DevOps.")

    conn = get_connection()
    df_esc = pd.read_sql_query("""
        SELECT id, ticket_id, risk_type, severity, customer_tier, reason, suggested_action, assigned_owner, status, created_at 
        FROM escalations 
        WHERE status = 'Escalated'
        ORDER BY id DESC
    """, conn)
    conn.close()

    if df_esc.empty:
        st.success("✅ Clean Slate! No active escalations require manager intervention.")
        return

    st.markdown(f"🚨 **Active Escalation Incidents:** {len(df_esc)}")

    # Show data table
    st.dataframe(
        df_esc[["ticket_id", "risk_type", "severity", "customer_tier", "reason", "suggested_action", "assigned_owner", "created_at"]],
        use_container_width=True,
        hide_index=True
    )

    # Resolution panel
    st.markdown("### Resolve Escalation Incident")
    c1, c2 = st.columns(2)
    with c1:
        target_esc_id = st.selectbox("Select Escalation (by Ticket ID):", df_esc["ticket_id"].tolist())
    with c2:
        res_note = st.text_input("Resolution Resolution Notes:", placeholder="Refund confirmed, user logged in")

    resolve_action = st.button("Resolve Incident", use_container_width=True)

    if resolve_action and target_esc_id:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update escalation status
        cursor.execute("UPDATE escalations SET status = 'Resolved' WHERE ticket_id = ?", (target_esc_id,))
        # Update ticket status in general table
        cursor.execute("UPDATE tickets SET escalation_status = 'Resolved', status = 'Resolved' WHERE ticket_id = ?", (target_esc_id,))
        
        conn.commit()
        log_audit("Resolve Escalation", f"Escalation for {target_esc_id} resolved", f"Resolution notes: {res_note}", "system", 0, "success")
        conn.close()
        st.success(f"Escalation for ticket {target_esc_id} has been resolved successfully!")
        st.rerun()
