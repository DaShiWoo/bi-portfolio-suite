# projects/fintech/__init__.py
import streamlit as st
from core.data_loader import load_fintech_transactions
from core.filters import build_fintech_filters
from projects.fintech import page1_command, page2_anomalies, page3_rails, page4_geo, page5_simulator

def render() -> None:
    df = load_fintech_transactions()
    df_f = build_fintech_filters(df, key_prefix="fin")
    
    tabs = st.tabs([
        "🛡️  1. Live Threat Command",
        "🕵️  2. Anomaly Investigation",
        "💳  3. Payment Channels & Rails",
        "🌍  4. Geolocation Risk Matrix",
        "⚙️  5. Rule Engine Simulator"
    ])
    
    with tabs[0]:
        page1_command.render(df_f)
    with tabs[1]:
        page2_anomalies.render(df_f)
    with tabs[2]:
        page3_rails.render(df_f)
    with tabs[3]:
        page4_geo.render(df_f)
    with tabs[4]:
        page5_simulator.render(df_f)
