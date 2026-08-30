# projects/gaming/__init__.py
import streamlit as st
import pandas as pd
from projects.gaming import page1_engagement, page2_funnel, page3_currency, page4_monetization, page5_retention

def render():
    df = pd.read_parquet("data/gaming_telemetry.parquet")
    
    tabs = st.tabs([
        "🎮  1. Player Engagement & DAU/MAU",
        "🧗  2. Level Progression & Churn Funnel",
        "🪙  3. Virtual Currency Sink vs Source",
        "🛒  4. Monetization & Whale Analytics",
        "⏱️  5. Retention Benchmark Simulator"
    ])
    
    with tabs[0]:
        page1_engagement.render(df)
    with tabs[1]:
        page2_funnel.render(df)
    with tabs[2]:
        page3_currency.render(df)
    with tabs[3]:
        page4_monetization.render(df)
    with tabs[4]:
        page5_retention.render(df)
