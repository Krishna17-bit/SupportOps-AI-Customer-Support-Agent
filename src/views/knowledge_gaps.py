import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from src.database import get_connection, save_article, log_audit

def render_knowledge_gaps():
    st.markdown("## Knowledge Gaps Analyzer")
    st.markdown("Monitor queries and topics where active support tickets did not find matching evidence in the library.")

    conn = get_connection()
    df_gaps = pd.read_sql_query("SELECT * FROM knowledge_gaps WHERE status = 'Open' ORDER BY affected_tickets_count DESC", conn)
    conn.close()

    if df_gaps.empty:
        st.success("✅ Awesome! All identified knowledge gaps have been successfully addressed.")
        return

    st.markdown(f"📊 **Identified KB Gaps:** Found {len(df_gaps)} documentation voids affecting support triage.")

    for idx, row in df_gaps.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div class="panel">
                    <div style="font-weight: 700; font-size: 1.05rem; color: #f97316;">Gap Topic: {row['query_text']}</div>
                    <b>Category:</b> {row['category']} | <b>Affected Tickets Ingested:</b> {row['affected_tickets_count']}<br>
                    <b>Automation Recommendation:</b> {row['recommendation']}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Drafting form
            col1, col2 = st.columns(2)
            with col1:
                art_id = f"KB-GAP-{row['id']}"
                draft_title = st.text_input("New Article Title", value=f"Guide: Troubleshooting {row['query_text']}", key=f"title_{row['id']}")
                draft_content = st.text_area("Draft Documentation Content", value=f"This guide addresses issues related to {row['query_text']}.\n\n### Steps:\n1. Verify connection credentials.\n2. Confirm webhook endpoint parameters.\n3. Restart client service integration.", key=f"content_{row['id']}")
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("Generate & Approve KB Article", key=f"gen_{row['id']}", use_container_width=True):
                    # Save to article database
                    new_art = {
                        "article_id": art_id,
                        "title": draft_title,
                        "content": draft_content,
                        "product_area": "System Additions",
                        "category": row["category"],
                        "tags": "gap-resolution",
                        "status": "approved",
                        "last_updated": datetime.now().strftime("%Y-%m-%d"),
                        "owner": "Agent Alpha",
                        "usage_count": 0,
                        "helpfulness_score": 5.0,
                        "source": "gap_auto_generator",
                        "visibility": "public",
                        "confidence_score": 1.0
                    }
                    save_article(new_art)
                    
                    # Update gap status to closed
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE knowledge_gaps SET status = 'Addressed' WHERE id = ?", (row["id"],))
                    conn.commit()
                    conn.close()
                    
                    log_audit("Address Knowledge Gap", f"Article {art_id} generated from gap log", f"Topic: {row['query_text']}", "system", 0, "success")
                    st.success(f"Article {art_id} generated and gap marked as Addressed!")
                    st.rerun()
                
                if st.button("Ignore Gap", key=f"ign_{row['id']}", use_container_width=True):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE knowledge_gaps SET status = 'Addressed' WHERE id = ?", (row["id"],))
                    conn.commit()
                    conn.close()
                    st.info("Gap ignored.")
                    st.rerun()

            st.divider()
