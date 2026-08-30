# projects/saas/__init__.py
import streamlit as st
from core.data_loader import load_saas_subscriptions
from core.filters import build_saas_filters
from projects.saas import page1_mrr, page2_nrr, page3_churn, page4_cac, page5_forecast

def render() -> None:
    df = load_saas_subscriptions()
    df_f = build_saas_filters(df, key_prefix="saas")
    
    tabs = st.tabs([
        "📈  1. MRR & ARR Growth Velocity",
        "🔄  2. NRR & Cohort Retention",
        "📉  3. Churn & Downgrades",
        "🎯  4. Acquisition Cost & Payback",
        "🔮  5. What-If Scenario Forecast"
    ])
    
    with tabs[0]:
        page1_mrr.render(df_f)
    with tabs[1]:
        page2_nrr.render(df_f)
    with tabs[2]:
        page3_churn.render(df_f)
    with tabs[3]:
        page4_cac.render(df_f)
    with tabs[4]:
        page5_forecast.render(df_f)
