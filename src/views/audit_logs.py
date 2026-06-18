import streamlit as st
import pandas as pd
import sqlite3
from src.database import get_connection, log_audit

def render_audit_logs():
    st.markdown("## Runs & Audit Logs")
    st.markdown("Review system executions, model latencies, token consumption, and analyst review decisions.")

    conn = get_connection()
    df_logs = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC", conn)
    conn.close()

    if df_logs.empty:
        st.info("No audit logs found.")
        return

    st.markdown(f"📋 **Total logs recorded:** {len(df_logs)} entries")

    # Action to clear logs
    if st.button("Clear System Audit Logs"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM audit_logs")
        cursor.execute("DELETE FROM run_logs")
        conn.commit()
        conn.close()
        st.success("All logs successfully cleared!")
        st.rerun()

    # Search query
    search_q = st.text_input("Filter logs by operation or ticket reference", "")
    if search_q:
        q = search_q.lower()
        df_logs = df_logs[
            df_logs["operation"].str.lower().str.contains(q) |
            df_logs["related_ticket_id"].str.lower().str.contains(q)
        ]

    # Data table display
    st.dataframe(
        df_logs[["id", "operation", "input_summary", "output_summary", "provider_model", "latency_ms", "status", "timestamp", "user_reviewer", "related_ticket_id"]],
        use_container_width=True,
        hide_index=True
    )
