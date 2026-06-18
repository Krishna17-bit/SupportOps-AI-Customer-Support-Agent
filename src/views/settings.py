import streamlit as st
import pandas as pd
import sqlite3
from src.database import get_connection, log_audit
from src.llm import AIEngine

def render_settings():
    st.markdown("## Settings & Provider Manager")
    st.markdown("Configure LLM model connections, input API credentials, adjust base URL parameters, and switch active providers.")

    # Load provider configurations
    conn = get_connection()
    df_prov = pd.read_sql_query("SELECT * FROM provider_settings", conn)
    conn.close()

    if df_prov.empty:
        st.error("No provider settings seeded in database.")
        return

    st.markdown("### Configured Model Providers")
    
    # Active Provider Selector
    active_options = df_prov["provider_name"].tolist()
    
    # Find currently active provider in DB
    active_prov = "mock"
    for idx, row in df_prov.iterrows():
        if row["is_active"] == 1:
            active_prov = row["provider_name"]
            break

    new_active = st.selectbox("Active Provider Analysis Mode:", active_options, index=active_options.index(active_prov))
    
    if st.button("Set Active Analysis Mode"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE provider_settings SET is_active = 0")
        cursor.execute("UPDATE provider_settings SET is_active = 1 WHERE provider_name = ?", (new_active,))
        conn.commit()
        conn.close()
        st.success(f"Analysis engine provider switched to '{new_active.upper()}'!")
        st.rerun()

    st.divider()
    st.markdown("### Edit Provider Credentials")
    
    # Form for editing a specific provider credentials
    target_prov = st.selectbox("Select Provider to configure:", active_options)
    prov_row = df_prov[df_prov["provider_name"] == target_prov].iloc[0]

    # Mask key
    stored_key = prov_row["api_key"] or ""
    masked_key = stored_key
    if stored_key and len(stored_key) > 8:
        masked_key = stored_key[:4] + "****" + stored_key[-4:]
    
    st.info(f"Currently configured model: `{prov_row['model_name'] or 'default'}`")
    
    new_key = st.text_input("API Access Key (leave empty or type to override):", value="", type="password", help="Input credentials key")
    new_model = st.text_input("LLM Model Name Identifier:", value=prov_row["model_name"] or "")
    new_url = st.text_input("API Base Endpoint URL (optional / local models):", value=prov_row["base_url"] or "")

    test_col, save_col = st.columns(2)

    # Instantiate LLM Engine to test connection
    ai_engine = AIEngine()

    with test_col:
        test_conn = st.button("Verify Connection", use_container_width=True)
        if test_conn:
            key_to_use = new_key if new_key else stored_key
            with st.spinner("Testing API connection safety gates..."):
                res = ai_engine.test_connection(target_prov, key_to_use, new_model, new_url)
                if res.ok:
                    st.success(f"Connection to '{target_prov.upper()}' verified successfully! {res.message}")
                else:
                    st.error(f"Verification Failed: {res.message}")

    with save_col:
        save_conn = st.button("Save Credentials Changes", use_container_width=True)
        if save_conn:
            key_to_save = new_key if new_key else stored_key
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE provider_settings 
                SET api_key = ?, model_name = ?, base_url = ?
                WHERE provider_name = ?
            """, (key_to_save, new_model, new_url, target_prov))
            conn.commit()
            conn.close()
            st.success(f"Updated configuration for '{target_prov.upper()}' in local storage!")
            log_audit("Update settings", f"Updated settings for {target_prov}", "", "system", 0, "success")
            st.rerun()
