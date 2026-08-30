# projects/healthtech/__init__.py
import streamlit as st
from core.data_loader import load_health_telemetry
from projects.healthtech import page1_icu, page2_vitals, page3_survival, page4_risk, page5_cohorts

def render() -> None:
    df = load_health_telemetry()
    
    tabs = st.tabs([
        "🏥  1. ICU Command & Bed Census",
        "💓  2. Cardiovascular Vitals Density",
        "⏳  3. Clinical Survival & Readmission",
        "⚠️  4. Patient Risk Stratification",
        "🧪  5. Clinical Cohort Explorer & What-If"
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
