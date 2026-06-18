import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from src.database import get_connection, save_article, log_audit

def render_knowledge_base():
    st.markdown("## Knowledge Base Library")
    st.markdown("Add, edit, approve, and manage documentation articles, FAQs, and policies referenced during reply grounding.")

    # Ingest forms
    with st.expander("📝 Add New KB Article"):
        art_id = st.text_input("Article ID (e.g., KB-211)", f"KB-{int(datetime.now().timestamp())%1000:03d}")
        art_title = st.text_input("Article Title", placeholder="How to configure custom webhook payloads")
        art_area = st.text_input("Product Area", placeholder="Integrations")
        art_cat = st.selectbox("Category Mapping", ["Refund / Return", "Account / Access", "Billing", "Delivery / Order Status", "Subscription / Cancellation", "Product Question", "Outage / Incident", "Complaint / Escalation", "General Support"])
        art_status = st.selectbox("Status", ["approved", "draft", "outdated", "needs review"])
        art_content = st.text_area("Article Markdown Content", placeholder="Write article content here...")
        
        submit_art = st.button("Add Article")
        if submit_art:
            if art_title and art_content:
                new_art = {
                    "article_id": art_id,
                    "title": art_title,
                    "content": art_content,
                    "product_area": art_area,
                    "category": art_cat,
                    "tags": art_area.lower(),
                    "status": art_status,
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "owner": "Agent Alpha",
                    "usage_count": 0,
                    "helpfulness_score": 5.0,
                    "source": "manual_entry",
                    "visibility": "public",
                    "confidence_score": 1.0
                }
                save_article(new_art)
                log_audit("Add KB Article", f"Article {art_id} created manually", f"Title: {art_title}", "system", 0, "success")
                st.success(f"Article {art_id} has been added successfully!")
                st.rerun()
            else:
                st.warning("Article Title and Content are required.")

    # Load from DB
    conn = get_connection()
    df_kb = pd.read_sql_query("SELECT * FROM knowledge_articles ORDER BY last_updated DESC", conn)
    conn.close()

    if df_kb.empty:
        st.info("No articles in database.")
        return

    # List articles
    st.markdown("### Active Articles Grid")
    for idx, row in df_kb.iterrows():
        with st.expander(f"{row['article_id']} · {row['title']} · [{row['status'].upper()}]"):
            st.markdown(f"**Product Area:** {row['product_area']} | **Category:** {row['category']} | **Owner:** {row['owner']}")
            st.markdown(f"**Last Updated:** {row['last_updated']} | **Usage Count:** {row['usage_count']}")
            st.markdown("---")
            st.markdown(row["content"])
            st.markdown("---")
            
            # Action Row
            col1, col2, col3 = st.columns(3)
            with col1:
                if row["status"] != "approved":
                    if st.button("Approve Article", key=f"app_{row['article_id']}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE knowledge_articles SET status = 'approved' WHERE article_id = ?", (row["article_id"],))
                        conn.commit()
                        conn.close()
                        st.success("Article status updated to Approved!")
                        st.rerun()
            with col2:
                if row["status"] != "outdated":
                    if st.button("Mark Outdated", key=f"out_{row['article_id']}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE knowledge_articles SET status = 'outdated' WHERE article_id = ?", (row["article_id"],))
                        conn.commit()
                        conn.close()
                        st.success("Article status marked Outdated!")
                        st.rerun()
            with col3:
                # Direct update content
                edited_content = st.text_area("Edit Content Link", value=row["content"], key=f"edit_txt_{row['article_id']}", label_visibility="collapsed")
                if st.button("Save Changes", key=f"save_edit_{row['article_id']}"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE knowledge_articles SET content = ? WHERE article_id = ?", (edited_content, row["article_id"]))
                    conn.commit()
                    conn.close()
                    st.success("Changes saved!")
                    st.rerun()
