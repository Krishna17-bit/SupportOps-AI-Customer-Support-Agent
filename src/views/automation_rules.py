import streamlit as st
import pandas as pd
import sqlite3
from src.database import get_connection, log_audit

def render_automation_rules():
    st.markdown("## Automation Rules and Playbooks")
    st.markdown("Establish support routing instructions, automated priority increments, and escalation policies.")

    # Form to add a rule
    with st.expander("⚙️ Create Automation Rule"):
        r_name = st.text_input("Rule Name", placeholder="Route critical bugs to support lead")
        
        c1, c2 = st.columns(2)
        with c1:
            cond_type = st.selectbox("Trigger Condition Type:", ["category", "sentiment", "urgency_score", "sla_risk", "safety_flags"])
            cond_val = st.text_input("Trigger Value (equals):", placeholder="Bug / Technical Issue")
        with c2:
            act_type = st.selectbox("Action Operation:", ["escalate", "route", "require_review", "redact", "suggest_macro"])
            act_val = st.text_input("Action Target / Group:", placeholder="DevOps Team")

        risk_level = st.selectbox("Rule Severity Risk Level:", ["Low", "Medium", "High", "Critical"])
        rule_owner = st.text_input("Owner Owner Team:", value="Ops Team")
        
        rule_submit = st.button("Activate Playbook Rule")
        
        if rule_submit:
            if r_name and cond_val and act_val:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO automation_rules (rule_name, condition_type, condition_value, action_type, action_value, is_enabled, risk_level, owner, trigger_count)
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?, 0)
                """, (r_name, cond_type, cond_val, act_type, act_val, risk_level, rule_owner))
                conn.commit()
                conn.close()
                
                log_audit("Create Automation Rule", f"Rule '{r_name}' added", f"Trigger: {cond_type}={cond_val}", "system", 0, "success")
                st.success(f"Rule '{r_name}' activated successfully!")
                st.rerun()
            else:
                st.warning("Please fill out Rule Name, Trigger Value, and Action Target.")

    # Load from DB
    conn = get_connection()
    df_rules = pd.read_sql_query("SELECT * FROM automation_rules ORDER BY id ASC", conn)
    conn.close()

    if df_rules.empty:
        st.info("No playbook rules configured.")
        return

    st.markdown("### Active Routing & Triage Rules")
    for idx, row in df_rules.iterrows():
        enabled_state = "Enabled" if row["is_enabled"] == 1 else "Disabled"
        with st.expander(f"⚙️ {row['rule_name']} · [{enabled_state.upper()}]"):
            st.markdown(f"**Condition:** If `{row['condition_type']}` == `{row['condition_value']}`")
            st.markdown(f"**Action Action:** {row['action_type'].upper()} -> `{row['action_value']}`")
            st.markdown(f"**Risk Level:** {row['risk_level']} | **Owner:** {row['owner']} | **Trigger Count:** {row['trigger_count']} times")
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                # Toggle enabled
                toggle_txt = "Disable Rule" if row["is_enabled"] == 1 else "Enable Rule"
                if st.button(toggle_txt, key=f"tog_{row['id']}"):
                    new_val = 0 if row["is_enabled"] == 1 else 1
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE automation_rules SET is_enabled = ? WHERE id = ?", (new_val, row["id"]))
                    conn.commit()
                    conn.close()
                    st.success("Rule status updated!")
                    st.rerun()
            with col2:
                if st.button("Delete Playbook Rule", key=f"del_rule_{row['id']}"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM automation_rules WHERE id = ?", (row["id"],))
                    conn.commit()
                    conn.close()
                    log_audit("Delete Automation Rule", f"Rule id {row['id']} deleted", "", "system", 0, "success")
                    st.success("Rule deleted.")
                    st.rerun()
                    
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
