import streamlit as st
import pandas as pd
import sqlite3
from src.database import get_connection

def render_customers():
    st.markdown("## Customer 360 Context")
    st.markdown("Profile accounts, check ARR metrics, renewal statuses, and review active support tickets mapped to clients.")

    conn = get_connection()
    df_cust = pd.read_sql_query("SELECT * FROM customers ORDER BY name ASC", conn)
    conn.close()

    if df_cust.empty:
        st.info("No customer records found in database.")
        return

    # Filter/Search
    search_q = st.text_input("🔍 Search CRM (name, company, email)", "")
    if search_q:
        q = search_q.lower()
        df_cust = df_cust[
            df_cust["name"].str.lower().str.contains(q) |
            df_cust["company"].str.lower().str.contains(q) |
            df_cust["email"].str.lower().str.contains(q)
        ]

    # Display list
    for idx, row in df_cust.iterrows():
        # Get active ticket counts for this customer
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tickets WHERE email = ?", (row["email"],))
        ticket_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT ticket_id, subject, status FROM tickets WHERE email = ? LIMIT 5", (row["email"],))
        tickets_list = cursor.fetchall()
        conn.close()

        # Alert colors for churn risk
        risk_color = "#10b981" # green
        if row["churn_risk"] >= 75:
            risk_color = "#ef4444" # red
        elif row["churn_risk"] >= 40:
            risk_color = "#f59e0b" # orange

        with st.expander(f"{row['name']} · {row['company']} · {row['tier']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f"""
                    **Email:** <a href="mailto:{row['email']}">{row['email']}</a><br>
                    **Company:** {row['company']}<br>
                    **Subscription Plan:** {row['plan']} ({row['arr_mrr']})<br>
                    **Renewal Date:** {row['renewal_date']}<br>
                    **SLA Policy Limit:** {row['sla_policy']}
                    """,
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f"""
                    **Customer CSAT:** {row['csat'] or "No score"} / 5.0<br>
                    **Account Churn Risk:** <span style="font-weight:700; color:{risk_color};">{row['churn_risk']}%</span><br>
                    **Total Tickets Ingested:** {ticket_count}<br>
                    **CRM Notes:** {row['notes'] or "No notes added"}
                    """,
                    unsafe_allow_html=True
                )
            
            # Show ticket list if any
            if tickets_list:
                st.markdown("**Recent Support Incidents:**")
                for tk in tickets_list:
                    st.markdown(f"- **{tk[0]}** (Status: {tk[2]}): {tk[1]}")
            else:
                st.write("No active support incidents logged.")
            
            # Action to edit notes
            new_notes = st.text_area("Update Client Notes", value=row["notes"] or "", key=f"notes_{row['email']}")
            if st.button("Apply CRM Notes", key=f"save_notes_{row['email']}"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE customers SET notes = ? WHERE email = ?", (new_notes, row["email"]))
                conn.commit()
                conn.close()
                st.success("Notes saved!")
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
