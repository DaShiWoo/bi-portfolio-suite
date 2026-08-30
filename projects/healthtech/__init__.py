# projects/healthtech/__init__.py
import streamlit as st
import pandas as pd
from projects.healthtech import page1_icu, page2_vitals, page3_survival, page4_risk, page5_cohorts

def render():
    df = pd.read_parquet("data/health_telemetry.parquet")
    
    tabs = st.tabs([
        "🏥  1. Clinical ICU Telemetry",
        "💓  2. Vitals Density & Telemetry",
        "💊  3. Treatment Efficacy & Survival",
        "⚠️  4. Patient Risk Stratification",
        "📋  5. Cohort Explorer & Discharge Simulator"
    ])
    
    with tabs[0]:
        page1_icu.render(df)
    with tabs[1]:
        page2_vitals.render(df)
    with tabs[2]:
        page3_survival.render(df)
    with tabs[3]:
        page4_risk.render(df)
    with tabs[4]:
        page5_cohorts.render(df)
