import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from src.database import get_connection, save_macro, log_audit

def render_macros():
    st.markdown("## Macro Library")
    st.markdown("Manage approved canned replies and text snippet patterns applied during review and agent copy processes.")

    # Form to add macro
    with st.expander("➕ Create New Macro"):
        m_id = st.text_input("Macro ID", f"M-1{int(datetime.now().timestamp())%1000:03d}")
        m_title = st.text_input("Macro Title", placeholder="Standard Bug acknowledgment response")
        m_cat = st.selectbox("Category", ["Refund / Return", "Account / Access", "Billing", "Delivery / Order Status", "Subscription / Cancellation", "Product Question", "Outage / Incident", "Complaint / Escalation", "General Support"])
        m_content = st.text_area("Canned Text Body", placeholder="Hi {{customer_name}}, thank you for notifying us...")
        
        m_submit = st.button("Create Macro")
        if m_submit:
            if m_title and m_content:
                new_mac = {
                    "macro_id": m_id,
                    "title": m_title,
                    "category": m_cat,
                    "content": m_content,
                    "approved_status": "approved",
                    "owner": "Agent Alpha",
                    "last_reviewed": datetime.now().strftime("%Y-%m-%d"),
                    "related_kb_articles": "",
                    "usage_count": 0,
                    "success_score": 5.0,
                    "risk_level": "Low",
                    "tags": m_cat.lower()
                }
                save_macro(new_mac)
                log_audit("Create Macro", f"Macro {m_id} created manually", f"Title: {m_title}", "system", 0, "success")
                st.success(f"Macro {m_id} has been added successfully!")
                st.rerun()
            else:
                st.warning("Macro Title and Content are required.")

    # Load from DB
    conn = get_connection()
    df_macros = pd.read_sql_query("SELECT * FROM macros ORDER BY macro_id ASC", conn)
    conn.close()

    if df_macros.empty:
        st.info("No macros in database.")
        return

    # List macros in cards
    st.markdown("### Approved Macros")
    for idx, row in df_macros.iterrows():
        with st.expander(f"{row['macro_id']} · {row['title']} · [{row['category']}]"):
            st.markdown(f"**Usage Count:** {row['usage_count']} times | **Risk Level:** {row['risk_level']}")
            st.markdown("---")
            st.text_area("Macro Text Template", value=row["content"], height=100, key=f"mac_txt_{row['macro_id']}")
            
            # Action Row
            col1, col2 = st.columns(2)
            with col1:
                # Save changes
                new_txt = st.session_state.get(f"mac_txt_{row['macro_id']}")
                if st.button("Update Content", key=f"upd_mac_{row['macro_id']}"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE macros SET content = ? WHERE macro_id = ?", (new_txt, row["macro_id"]))
                    conn.commit()
                    conn.close()
                    st.success("Macro updated!")
                    st.rerun()
            with col2:
                if st.button("Delete Macro", key=f"del_mac_{row['macro_id']}"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM macros WHERE macro_id = ?", (row["macro_id"],))
                    conn.commit()
                    conn.close()
                    log_audit("Delete Macro", f"Macro {row['macro_id']} deleted", "", "system", 0, "success")
                    st.success("Macro deleted!")
                    st.rerun()
