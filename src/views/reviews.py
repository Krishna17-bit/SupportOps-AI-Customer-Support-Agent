import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from src.database import get_connection, log_audit

def render_reviews():
    st.markdown("## Review Queue")
    st.markdown("Inspect and approve AI-generated reply drafts, refund decisions, and customer save offers prior to external dispatch.")

    conn = get_connection()
    # Query tickets that are open/new and flagged for escalation, or have low confidence
    df_reviews = pd.read_sql_query("""
        SELECT ticket_id, customer_name, subject, category, qa_score, resolution_confidence, suggested_reply, internal_note 
        FROM tickets 
        WHERE escalation_status = 'Escalated' OR resolution_confidence < 75 OR category IN ('Refund / Return', 'Complaint / Escalation')
    """, conn)
    conn.close()

    if df_reviews.empty:
        st.success("🎉 All clear! The review queue is empty. No drafts require human validation.")
        return

    st.markdown(f"📝 **Items Awaiting Validation:** {len(df_reviews)}")

    # Show review cards
    for idx, row in df_reviews.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div class="panel">
                    <div style="font-weight: 700; font-size: 1.1rem; color: #0f62fe;">Ticket ID: {row['ticket_id']} · {row['customer_name']}</div>
                    <b>Subject:</b> {row['subject']}<br>
                    <b>Category:</b> {row['category']} | <b>QA Score:</b> {row['qa_score']}% | <b>Resolution Confidence:</b> {row['resolution_confidence']}%<br>
                    <div class="small-muted" style="margin-top: 6px;"><b>Reviewer Note:</b> {row['internal_note']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Review editing area
            reply_draft = st.text_area("Review Response Content", value=row["suggested_reply"], height=160, key=f"rev_draft_{row['ticket_id']}")
            
            # Review decision comment
            rev_comment = st.text_input("Decision Comment (optional)", placeholder="Tone is excellent, policy matches", key=f"rev_com_{row['ticket_id']}")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Approve Reply", key=f"app_btn_{row['ticket_id']}"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO review_decisions (item_type, item_id, decision, comment, reviewer, timestamp)
                        VALUES ('reply', ?, 'approved', ?, 'QA Lead', ?)
                    """, (row["ticket_id"], rev_comment or "Approved without comments", datetime.now().isoformat()))
                    cursor.execute("UPDATE tickets SET suggested_reply = ?, status = 'Resolved', escalation_status = 'None' WHERE ticket_id = ?", (reply_draft, row["ticket_id"]))
                    conn.commit()
                    conn.close()
                    log_audit("Approve Reply", f"Ticket ID {row['ticket_id']} approved", "Status updated to Resolved", "system", 0, "success")
                    st.success("Draft reply approved!")
                    st.rerun()
            with col2:
                if st.button("Reject Draft", key=f"rej_btn_{row['ticket_id']}"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO review_decisions (item_type, item_id, decision, comment, reviewer, timestamp)
                        VALUES ('reply', ?, 'rejected', ?, 'QA Lead', ?)
                    """, (row["ticket_id"], rev_comment or "Draft rejected", datetime.now().isoformat()))
                    cursor.execute("UPDATE tickets SET escalation_status = 'None', status = 'Open', internal_note = 'Draft rejected. Please rewrite manually.' WHERE ticket_id = ?", (row["ticket_id"],))
                    conn.commit()
                    conn.close()
                    log_audit("Reject Reply", f"Ticket ID {row['ticket_id']} draft rejected", "Status updated to Open", "system", 0, "success")
                    st.warning("Draft rejected. Ticket returned to primary agent queue.")
                    st.rerun()
            with col3:
                st.download_button(
                    "Download Output Text",
                    data=reply_draft,
                    file_name=f"Approved_{row['ticket_id']}_reply.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            st.divider()
