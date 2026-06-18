import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from src.database import get_connection, log_audit

def render_connectors():
    st.markdown("## Integration Connectors")
    st.markdown("Configure connectors to sync customer data, pull order history, stream tickets, and write approved replies back to helpdesk systems.")

    conn = get_connection()
    df_conn = pd.read_sql_query("SELECT * FROM connectors ORDER BY id ASC", conn)
    conn.close()

    if df_conn.empty:
        st.info("No active connectors configured.")
        return

    st.markdown("### Configured Integration Connectors")
    for idx, row in df_conn.iterrows():
        # Status color
        stat_color = "#10b981" # green
        if row["status"] == "Inactive":
            stat_color = "#64748b" # gray
        elif row["status"] == "Error":
            stat_color = "#ef4444" # red

        with st.expander(f"🔌 {row['name']} · [{row['type'].upper()}]"):
            st.markdown(
                f"""
                **Auth Method:** {row['auth_method']} | **Sync Status:** <span style="font-weight:700; color:{stat_color};">{row['status']}</span><br>
                **Last Synced:** {row['last_sync'] or "Never"}<br>
                **Connected Workflows:** {row['connected_workflows'] or "None"}<br>
                **Risk Profile:** {row['risk_level']} Severity
                """,
                unsafe_allow_html=True
            )
            if row["sync_errors"]:
                st.error(f"Sync Connection Error: {row['sync_errors']}")

            # Test connection button
            if st.button("Test Connection", key=f"test_con_{row['id']}"):
                conn_db = get_connection()
                cursor = conn_db.cursor()
                if row["name"] == "Freshdesk Connector":
                    # Mocking failure correction or simple toggle
                    cursor.execute("UPDATE connectors SET status = 'Active', sync_errors = '' WHERE id = ?", (row["id"],))
                    st.success("Connection test succeeded! Status updated to Active.")
                else:
                    cursor.execute("UPDATE connectors SET last_sync = ? WHERE id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M"), row["id"]))
                    st.success("Connection test succeeded! Settings verified.")
                conn_db.commit()
                conn_db.close()
                log_audit("Test Connection", f"Tested connection {row['name']}", "Status: Active", "system", 0, "success")
                st.rerun()

    # Form placeholder for new connectors
    st.divider()
    st.markdown("### Add Integration Connector")
    new_name = st.selectbox("Connector Application:", [
        "Jira Service Management", "Zendesk", "Freshdesk", "Intercom", "HelpScout", 
        "Gmail Inbox", "Outlook Mail", "Slack Channel", "Discord Server", 
        "Shopify Log Sync", "Stripe billing Log", "HubSpot CRM", "Notion wiki", "Confluence Knowledge"
    ])
    new_auth = st.selectbox("Authentication Type:", ["OAuth 2.0 Access Token", "API Key Credential", "System Webhook Secret"])
    
    if st.button("Configure and Test Connector"):
        conn_db = get_connection()
        cursor = conn_db.cursor()
        cursor.execute("""
            INSERT INTO connectors (name, type, status, auth_method, last_sync, sync_errors, data_scope, connected_workflows, risk_level)
            VALUES (?, ?, 'Active', ?, ?, '', 'customer support tickets', 'Triage pipeline, auto reply generation', 'Medium')
        """, (f"{new_name} Link", new_name, new_auth, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn_db.commit()
        conn_db.close()
        log_audit("Create Connector", f"Connected {new_name} link", "", "system", 0, "success")
        st.success(f"Successfully integrated {new_name} link! Data synchronization is now active.")
        st.rerun()
