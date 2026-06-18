import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from src.database import get_connection, log_audit

def render_qa_review():
    st.markdown("## Support QA and Reply Review")
    st.markdown("Review support agent interactions, evaluate reply accuracy, verify policy compliance, and audit grounding parameters.")

    # Form to review a reply manually
    with st.expander("🔍 Start New Reply QA Review"):
        t_id = st.text_input("Review Ticket ID", placeholder="T-1001")
        agent_reply = st.text_area("Agent Reply Text to Audit", placeholder="Write reply content...")
        
        st.markdown("**QA Checklist Criteria**")
        c1, c2 = st.columns(2)
        with c1:
            q_acc = st.slider("Accuracy Score (facts match policy)", 0, 100, 80)
            q_emp = st.slider("Empathy & Tone Score", 0, 100, 80)
        with c2:
            q_comp = st.slider("Completeness (addresses all questions)", 0, 100, 80)
            policy_ok = st.checkbox("Strict Policy Compliance (no unsafe promises)", value=True)

        qa_issues = st.text_input("Identified Issues / Improvements", placeholder="Forgot to thank the client, missing tracking number reference")
        suggested_fix = st.text_area("Suggested Rewrite", placeholder="Write improved response...")
        
        submit_qa = st.button("Submit QA scorecard")
        
        if submit_qa:
            if t_id and agent_reply:
                overall_score = int((q_acc + q_emp + q_comp) / 3)
                if not policy_ok:
                    overall_score = min(40, overall_score) # penalty for compliance failure
                
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO qa_reviews (ticket_id, qa_score, accuracy_score, empathy_score, completeness_score, policy_compliance, issues_detected, suggested_rewrite, status, reviewer, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'reviewed', 'QA Auditor', ?)
                """, (t_id, overall_score, q_acc, q_emp, q_comp, "Pass" if policy_ok else "Fail", qa_issues, suggested_fix, datetime.now().isoformat()))
                conn.commit()
                conn.close()
                
                log_audit("QA Scorecard Submitted", f"Audited ticket {t_id}", f"Overall Score: {overall_score}%", "system", 0, "success")
                st.success(f"QA Scorecard for {t_id} submitted with score {overall_score}%!")
                st.rerun()
            else:
                st.warning("Ticket ID and Agent Reply are required.")

    # Past reviews list
    st.markdown("### Past QA Audits")
    conn = get_connection()
    df_qa = pd.read_sql_query("SELECT * FROM qa_reviews ORDER BY id DESC", conn)
    conn.close()

    if df_qa.empty:
        st.info("No past QA scorecards logged in database.")
        return

    st.dataframe(
        df_qa[["id", "ticket_id", "qa_score", "accuracy_score", "empathy_score", "completeness_score", "policy_compliance", "issues_detected", "reviewer", "created_at"]],
        use_container_width=True,
        hide_index=True
    )
