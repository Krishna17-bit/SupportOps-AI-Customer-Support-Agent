import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from src.database import get_connection, log_audit

def render_churn_risk():
    st.markdown("## Churn Risk Detector")
    st.markdown("Identify accounts showing indicators of frustration, billing disputes, or competitor references.")

    conn = get_connection()
    df_churn = pd.read_sql_query("""
        SELECT ticket_id, customer_name, email, subject, sentiment, churn_risk, status 
        FROM tickets 
        WHERE churn_risk >= 50
        ORDER BY churn_risk DESC
    """, conn)
    conn.close()

    if df_churn.empty:
        st.success("✅ Excellent! No active tickets show high churn risk indicators.")
        return

    st.markdown(f"📊 **Accounts At Risk:** Found {len(df_churn)} tickets indicating moderate-to-severe retention risk.")

    # Search bar
    search_q = st.text_input("Filter Churn Queue by Customer Name/Email", "")
    if search_q:
        q = search_q.lower()
        df_churn = df_churn[
            df_churn["customer_name"].str.lower().str.contains(q) |
            df_churn["email"].str.lower().str.contains(q)
        ]

    # Show data table
    st.dataframe(
        df_churn[["ticket_id", "customer_name", "email", "subject", "sentiment", "churn_risk", "status"]],
        use_container_width=True,
        hide_index=True
    )

    # Actions panel
    st.markdown("### Client Save Actions")
    sc1, sc2 = st.columns(2)
    with sc1:
        target_ticket = st.selectbox("Select Customer Ticket ID:", df_churn["ticket_id"].tolist())
    with sc2:
        action_type = st.selectbox("Save Action Type:", [
            "Send Retention Downgrade Offer",
            "Escalate directly to Customer Success Director",
            "Schedule Emergency Account Review Call"
        ])

    trigger_action = st.button("Trigger Retention Action", use_container_width=True)

    if trigger_action and target_ticket:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Apply macro template depending on selected save action
        if "Retention Downgrade Offer" in action_type:
            cursor.execute("SELECT customer_name FROM tickets WHERE ticket_id = ?", (target_ticket,))
            cust_name = cursor.fetchone()[0]
            offer_text = (
                f"Hi {cust_name},\n\nI understand that our pricing or features have caused some friction recently. "
                "To help resolve this, I've added a complimentary 1-month credit to your account. Let me know if you would like "
                "to hop on a call to audit your team configuration details.\n\nBest regards,\nCustomer Retention Team"
            )
            cursor.execute("UPDATE tickets SET suggested_reply = ?, escalation_status = 'Escalated' WHERE ticket_id = ?", (offer_text, target_ticket))
            st.success(f"Grounded Retention Reply has been drafted and applied to ticket {target_ticket}!")
        else:
            # Save into escalations table
            cursor.execute("""
                INSERT INTO escalations (ticket_id, risk_type, severity, time_remaining, customer_tier, reason, suggested_action, assigned_owner, status, created_at)
                VALUES (?, 'Churn Prevention', 'Critical', '4 hours', 'Enterprise', ?, ?, 'Customer Success Lead', 'Escalated', ?)
            """, (target_ticket, f"Churn threat on ticket", action_type, datetime.now().isoformat()))
            st.success(f"Ticket {target_ticket} has been escalated to Customer Success Team for emergency handling.")
        
        conn.commit()
        log_audit("Churn Retention Action", f"Applied retention action on ticket {target_ticket}", f"Action: {action_type}", "system", 0, "success")
        conn.close()
        st.rerun()
