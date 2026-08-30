# projects/fintech/__init__.py
import streamlit as st
import pandas as pd
from projects.fintech import page1_command, page2_anomalies, page3_rails, page4_geo, page5_simulator

def render():
    df = pd.read_parquet("data/fintech_transactions.parquet")
    
    tabs = st.tabs([
        "🛡️  1. Live Threat Command",
        "🕵️  2. Anomaly Investigation",
        "💳  3. Payment Channels & Rails",
        "🌍  4. Geolocation Risk Matrix",
        "⚙️  5. Rule Engine Simulator"
    ])
    
    with tabs[0]:
        page1_command.render(df)
    with tabs[1]:
        page2_anomalies.render(df)
    with tabs[2]:
        page3_rails.render(df)
    with tabs[3]:
        page4_geo.render(df)
    with tabs[4]:
        page5_simulator.render(df)
