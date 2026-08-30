# projects/gaming/__init__.py
import streamlit as st
from core.data_loader import load_gaming_telemetry
from core.filters import build_gaming_filters
from projects.gaming import page1_engagement, page2_funnel, page3_currency, page4_monetization, page5_retention

def render() -> None:
    df = load_gaming_telemetry()
    df_f = build_gaming_filters(df, key_prefix="game")
    
    tabs = st.tabs([
        "🎮  1. Engagement & Active Cohorts",
        "🪜  2. Level Progression & Churn Walls",
        "🪙  3. Virtual Economy & Inflation Sink",
        "💎  4. Whale Monetization & LTV",
        "🔄  5. Retention Curve What-If Simulator"
    ])
    
    with tabs[0]:
        page1_engagement.render(df_f)
    with tabs[1]:
        page2_funnel.render(df_f)
    with tabs[2]:
        page3_currency.render(df_f)
    with tabs[3]:
        page4_monetization.render(df_f)
    with tabs[4]:
        page5_retention.render(df_f)
