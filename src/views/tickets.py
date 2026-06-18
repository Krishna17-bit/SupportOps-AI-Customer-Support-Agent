import streamlit as st
import pandas as pd
import sqlite3
import json
from datetime import datetime
from src.database import get_connection, save_ticket, log_audit
from src.llm import AIEngine
from src.data_loader import normalize_ticket_columns
from src.analysis_engine import analyze_tickets

def render_tickets():
    st.markdown("## Ticket Inbox")

    # Ticket intake controls
    with st.expander("📥 Ingest Support Tickets"):
        c1, c2 = st.columns([2, 1])
        with c1:
            ticket_file = st.file_uploader(
                "Upload tickets file (CSV / XLSX / JSON)",
                type=["csv", "xlsx", "json"],
                key="inbox_uploader"
            )
        with c2:
            st.markdown("**Manual Ingest Form**")
            m_id = st.text_input("Ticket ID", placeholder="T-1051", value=f"T-10{int(datetime.now().timestamp())%1000:03d}")
            m_cust = st.text_input("Customer Name", placeholder="Jane Doe")
            m_email = st.text_input("Customer Email", placeholder="jane@example.com")
            m_subj = st.text_input("Subject", placeholder="Unable to sync database")
            m_body = st.text_area("Body / Conversation Text", placeholder="Describe the issue...")
            m_submit = st.button("Add Manual Ticket")

        if ticket_file:
            try:
                raw = ticket_file.read()
                suffix = ticket_file.name.split(".")[-1].lower()
                from io import BytesIO
                if suffix == "csv":
                    df = pd.read_csv(BytesIO(raw))
                elif suffix in ["xlsx", "xls"]:
                    df = pd.read_excel(BytesIO(raw))
                elif suffix == "json":
                    df = pd.read_json(BytesIO(raw))

                df_normalized = normalize_ticket_columns(df)
                
                # Fetch knowledge base articles from DB
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT title, content, category FROM knowledge_articles")
                articles = []
                from src.data_loader import KnowledgeDoc
                for row in cursor.fetchall():
                    articles.append(KnowledgeDoc(row[0], row[1], "document", {"category": row[2]}))
                
                # Fetch order history
                cursor.execute("SELECT * FROM tickets LIMIT 1") # dummy query to check connection
                conn.close()
                
                order_history = pd.DataFrame(columns=["order_id", "order_date", "customer_email", "amount", "status", "delivered_date"])
                
                ai_engine = AIEngine()
                with st.spinner("Triaging uploaded tickets..."):
                    results_df, audit = analyze_tickets(
                        tickets_df=df_normalized,
                        docs=articles,
                        order_history=order_history,
                        ai_engine=ai_engine,
                        max_tickets=50
                    )
                st.success(f"Successfully ingested and triaged {len(results_df)} tickets from file!")
            except Exception as e:
                st.error(f"Error parsing file: {e}")

        if m_submit:
            if m_cust and m_email and m_subj and m_body:
                new_t = {
                    "ticket_id": m_id,
                    "customer_name": m_cust,
                    "email": m_email,
                    "subject": m_subj,
                    "body": m_body,
                    "channel": "manual_entry",
                    "status": "New",
                    "priority": "Medium",
                    "category": "General Support",
                    "intent": "General Support Intent",
                    "sentiment": "Neutral",
                    "sla_due_time": (datetime.now() + pd.Timedelta(hours=24)).strftime("%Y-%m-%d %H:%M"),
                    "sla_risk": "Low SLA risk",
                    "churn_risk": 15,
                    "assigned_team": "Triage Pool",
                    "assigned_agent": "",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "last_updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "order_id": "",
                    "latest_message": m_body,
                    "conversation_summary": m_subj,
                    "suggested_reply": f"Hi {m_cust},\n\nThank you for reaching out. We have received your query regarding '{m_subj}' and are looking into it.\n\nBest regards,\nSupportOps Team",
                    "linked_kb_article_id": "",
                    "escalation_status": "None",
                    "tags": "manual",
                    "internal_note": "Manual ingestion entry.",
                    "missing_info": "",
                    "safety_flags": "",
                    "qa_score": 85,
                    "resolution_confidence": 70,
                    "used_ai_refinement": 0
                }
                save_ticket(new_t)
                log_audit("Manual ticket ingest", f"Ticket ID {m_id} created manually", "Persisted ticket to database", "system", 0, "success")
                st.success(f"Manual ticket {m_id} added successfully!")
            else:
                st.warning("Please fill out customer name, email, subject, and body.")

    # Search and filter settings
    st.markdown("### Ingested Tickets List")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search Tickets (subject, body, customer, email)", "")
    with col2:
        filter_cat = st.selectbox("Category", ["All", "Refund / Return", "Account / Access", "Billing", "Bug / Technical Issue", "Delivery / Order Status", "Product Question", "Outage / Incident", "Complaint / Escalation", "General Support"])
    with col3:
        filter_status = st.selectbox("Status", ["All", "New", "Open", "Resolved"])
    with col4:
        filter_esc = st.selectbox("Escalation", ["All", "Escalated", "None"])

    # Load from DB
    conn = get_connection()
    df_db = pd.read_sql_query("SELECT * FROM tickets ORDER BY created_at DESC", conn)
    conn.close()

    if df_db.empty:
        st.info("No tickets in database. Try running analysis or adding a ticket manually.")
        return

    # Apply filters
    filtered_df = df_db.copy()
    if search_query:
        q = search_query.lower()
        filtered_df = filtered_df[
            filtered_df["subject"].str.lower().str.contains(q) |
            filtered_df["body"].str.lower().str.contains(q) |
            filtered_df["customer_name"].str.lower().str.contains(q) |
            filtered_df["email"].str.lower().str.contains(q)
        ]
    if filter_cat != "All":
        filtered_df = filtered_df[filtered_df["category"] == filter_cat]
    if filter_status != "All":
        filtered_df = filtered_df[filtered_df["status"] == filter_status]
    if filter_esc != "All":
        filtered_df = filtered_df[filtered_df["escalation_status"] == filter_esc]

    if filtered_df.empty:
        st.warning("No tickets match the selected filters.")
        return

    # Inbox layout: List on left, details drawer on right
    l_panel, r_panel = st.columns([1, 2])

    with l_panel:
        st.markdown(f"**Ingested Queue ({len(filtered_df)} items)**")
        
        # Build ticket card selections
        choices = []
        for idx, row in filtered_df.iterrows():
            choices.append(f"{row['ticket_id']} · {row['customer_name']} · {row['category'][:20]}")
        
        selected_choice = st.radio("Select a ticket to inspect:", choices, label_visibility="collapsed")
        
        # Parse selected ticket
        selected_id = selected_choice.split(" · ")[0]
        ticket_row = filtered_df[filtered_df["ticket_id"] == selected_id].iloc[0]

    with r_panel:
        st.markdown(f"### Ticket detail · **{ticket_row['ticket_id']}**")
        st.markdown(f"**Subject:** {ticket_row['subject']}")
        
        # Action Bar
        act_col1, act_col2, act_col3, act_col4 = st.columns(4)
        with act_col1:
            t_status = st.selectbox("Status", ["New", "Open", "Resolved"], index=["New", "Open", "Resolved"].index(ticket_row["status"]), key="status_box")
        with act_col2:
            t_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"], index=["Low", "Medium", "High", "Urgent"].index(ticket_row["priority"]), key="priority_box")
        with act_col3:
            t_escalate = st.selectbox("Escalation", ["None", "Escalated", "Resolved"], index=["None", "Escalated", "Resolved"].index(ticket_row["escalation_status"]), key="escalate_box")
        with act_col4:
            t_save = st.button("Apply Actions", use_container_width=True)

        if t_save:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tickets 
                SET status = ?, priority = ?, escalation_status = ?, last_updated_at = ?
                WHERE ticket_id = ?
            """, (t_status, t_priority, t_escalate, datetime.now().strftime("%Y-%m-%d %H:%M"), ticket_row["ticket_id"]))
            conn.commit()
            conn.close()
            st.success("Ticket parameters updated!")
            st.rerun()

        # Tabs Layout inside ticket detail
        t_tabs = st.tabs([
            "Overview", 
            "Conversation", 
            "AI Triage", 
            "Suggested Reply", 
            "KB Sources", 
            "SLA / Churn Risk", 
            "Internal Notes"
        ])

        with t_tabs[0]:
            st.markdown("#### Overview & CRM Profile")
            st.markdown(
                f"""
                <div class="panel">
                    <b>Customer:</b> {ticket_row['customer_name']} (<a href="mailto:{ticket_row['email']}">{ticket_row['email']}</a>)<br>
                    <b>Account Plan:</b> Pro Tier (Active)<br>
                    <b>Assigned Team:</b> {ticket_row['assigned_team'] or "None"}<br>
                    <b>Channel:</b> {ticket_row['channel'].upper()}<br>
                    <b>Ingested At:</b> {ticket_row['created_at']}<br>
                    <b>Order reference:</b> {ticket_row['order_id'] or "No order linked"}
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("#### Original Message Description")
            st.text_area("Customer text body", value=ticket_row["body"], height=160, disabled=True)

        with t_tabs[1]:
            st.markdown("#### Conversation Thread history")
            # Fetch message list from ticket_messages
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT sender, message_text, created_at FROM ticket_messages WHERE ticket_id = ?", (ticket_row["ticket_id"],))
            messages = cursor.fetchall()
            conn.close()

            if messages:
                for msg in messages:
                    st.markdown(
                        f"""
                        <div class="panel-compact" style="background: {'#f1f5f9' if msg[0]=='Customer' else '#eff6ff'};">
                            <b>{msg[0]}</b> · <span class="small-muted">{msg[2]}</span><br>
                            <span style="font-size: 0.9rem;">{msg[1]}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    f"""
                    <div class="panel-compact" style="background: #f1f5f9;">
                        <b>Customer</b> · <span class="small-muted">{ticket_row['created_at']}</span><br>
                        <span style="font-size: 0.9rem;">{ticket_row['body']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Summarizer button
            if st.button("Generate Thread Summary", key="sum_btn"):
                # Run thread summarizing
                summary_text = f"Customer requests assistance for {ticket_row['category']}. The ticket contains a reported message: '{ticket_row['body'][:80]}...' "
                if ticket_row["order_id"]:
                    summary_text += f"Linked Order is {ticket_row['order_id']}."
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE tickets SET conversation_summary = ? WHERE ticket_id = ?", (summary_text, ticket_row["ticket_id"]))
                conn.commit()
                conn.close()
                st.success("Thread summary generated!")
                st.markdown(f"**Summary:** {summary_text}")

        with t_tabs[2]:
            st.markdown("#### AI Triage Pipeline Results")
            st.markdown(
                f"""
                <div class="panel">
                    <b>Category:</b> {ticket_row['category']}<br>
                    <b>Intent:</b> {ticket_row['intent'] or "Not computed"}<br>
                    <b>Sentiment:</b> {ticket_row['sentiment']} (Urgency Score: {ticket_row['urgency_score']}/100)<br>
                    <b>Resolution Confidence:</b> {ticket_row['resolution_confidence']}%<br>
                    <b>Used AI Refinement:</b> {'Yes (LLM grounded)' if ticket_row['used_ai_refinement'] else 'No (Heuristics fallbacks)'}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Show safety flags & warnings
            if ticket_row["safety_flags"]:
                st.error(f"🚨 **Safety Alert Flags:** {ticket_row['safety_flags']}")
            else:
                st.success("✅ No prompt injections, card details, or PII leaks detected.")

            if ticket_row["missing_info"]:
                st.warning(f"⚠️ **Missing information needed:** {ticket_row['missing_info']}")

        with t_tabs[3]:
            st.markdown("#### Grounds Drafted reply")
            
            # Tone options
            tone = st.selectbox("Reply Tone Mode", ["Friendly", "Professional", "Concise", "Empathetic", "Technical", "Executive/VIP"])
            
            # Text area for actual reply
            suggested_reply_text = st.text_area(
                "Suggested response draft (Manual editing allowed)",
                value=ticket_row["suggested_reply"],
                height=220,
                key="edit_reply_area"
            )

            # Accept/Reject actions
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("Approve Reply & Queue for Dispatch", use_container_width=True):
                    # Write review decision
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO review_decisions (item_type, item_id, decision, comment, reviewer, timestamp)
                        VALUES ('reply', ?, 'approved', 'Approved from tickets inbox page', 'Agent Alpha', ?)
                    """, (ticket_row["ticket_id"], datetime.now().isoformat()))
                    cursor.execute("UPDATE tickets SET suggested_reply = ? WHERE ticket_id = ?", (suggested_reply_text, ticket_row["ticket_id"]))
                    conn.commit()
                    conn.close()
                    st.success("Reply successfully approved and added to review history!")
            with cc2:
                st.download_button(
                    "Download Reply TXT",
                    data=suggested_reply_text,
                    file_name=f"{ticket_row['ticket_id']}_suggested_reply.txt",
                    mime="text/plain",
                    use_container_width=True
                )

        with t_tabs[4]:
            st.markdown("#### Referenced Evidence Sources")
            
            # In mock or database, link articles
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT article_id, title, content FROM knowledge_articles WHERE category = ?", (ticket_row["category"],))
            articles = cursor.fetchall()
            conn.close()

            if articles:
                for art in articles:
                    st.markdown(
                        f"""
                        <div class="evidence">
                            <b>{art[0]} · {art[1]}</b><br>
                            <span>{art[2][:600]}...</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.warning("No high-confidence policy or faq documentation is linked to this ticket's category.")

        with t_tabs[5]:
            st.markdown("#### SLA & Churn Risk Metrics")
            st.markdown(
                f"""
                <div class="panel">
                    <b>SLA Risk Rating:</b> {ticket_row['sla_risk']}<br>
                    <b>Urgency Weight:</b> {ticket_row['urgency_score']} / 100<br>
                    <b>Target Response Deadline:</b> {ticket_row['sla_due_time'] or "24h default"}<br>
                    <b>Customer Churn Risk Level:</b> {ticket_row['churn_risk']} / 100
                </div>
                """,
                unsafe_allow_html=True
            )
            # Add retaining suggestions
            if ticket_row["churn_risk"] >= 50:
                st.error("⚠️ Customer displays high churn indicators (cancellation mentions or negative feedback).")
                st.info("💡 **Recommended retention offer:** Apply the 'Retention Downgrade Offer' macro to waive the monthly fee.")

        with t_tabs[6]:
            st.markdown("#### Internal Triage & Audit Notes")
            note_content = st.text_area("Internal analyst notes", value=ticket_row["internal_note"] or "")
            if st.button("Save Internal Notes"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE tickets SET internal_note = ? WHERE ticket_id = ?", (note_content, ticket_row["ticket_id"]))
                conn.commit()
                conn.close()
                st.success("Internal note saved successfully!")
