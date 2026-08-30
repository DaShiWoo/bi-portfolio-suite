# projects/saas/__init__.py
import streamlit as st
from core.data_loader import load_saas_subscriptions
from projects.saas import page1_mrr, page2_nrr, page3_churn, page4_cac, page5_forecast

def render() -> None:
    df = load_saas_subscriptions()
    
    tabs = st.tabs([
        "📈  1. MRR & ARR Growth Velocity",
        "🔄  2. NRR & Cohort Retention",
        "📉  3. Churn & Downgrades",
        "🎯  4. Acquisition Cost & Payback",
        "🔮  5. What-If Scenario Forecast"
    ])
    
    with tabs[0]:
        page1_mrr.render(df)
    with tabs[1]:
        page2_nrr.render(df)
    with tabs[2]:
        page3_churn.render(df)
    with tabs[3]:
        page4_cac.render(df)
    with tabs[4]:
        page5_forecast.render(df)
