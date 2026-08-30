# projects/healthtech/page5_cohorts.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Cohort Explorer & ICU Discharge Simulator", badge="PREDICTIVE SIMULATOR", subtitle="Filter custom patient sub-cohorts, analyze vitals distribution, and simulate discharge criteria")
    
    st.markdown("""
    <div class="what-if-container">
        <span style="font-weight: 700; color: #14b8a6; font-size: 0.95rem;">🔮 INTERACTIVE WHAT-IF SCENARIO: SAFE DISCHARGE SPO2 THRESHOLD</span>
        <div style="font-size: 0.8rem; color: #99f6e4; margin-top: 4px;">Simulate how raising the minimum SpO2 threshold for step-down transfer impacts readmission rates:</div>
    </div>
    """, unsafe_allow_html=True)
    
    min_spo2 = st.slider("Target SpO2 Discharge Cutoff (%)", min_value=92.0, max_value=98.0, value=95.0, step=0.5)
    
    cleared_pts = df[df["spo2"] >= min_spo2]
    readmit_rate = max(4.0, 16.0 - (min_spo2 - 92.0) * 1.8)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi("Eligible for Step-Down", f"{len(cleared_pts):,}", delta=f"{(len(cleared_pts)/len(df)*100):.1f}% of total census", is_positive=True, badge="TRANSFER")
    with c2:
        render_kpi("Simulated 30d Readmission", f"{readmit_rate:.1f}%", delta=f"-{(16.0-readmit_rate):.1f}% vs baseline", is_positive=True, badge="SAFETY")
    with c3:
        render_kpi("ICU Bed Capacity Released", f"{int(len(cleared_pts)*0.22):,} beds", delta="+18% availability", is_positive=True, badge="CAPACITY")
        
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>PATIENT COHORT RECORD EXPLORER</div>", unsafe_allow_html=True)
    st.dataframe(
        cleared_pts[["patient_id", "admit_date", "age", "gender", "ward", "risk_category", "spo2", "heart_rate", "bp_systolic"]].head(20),
        use_container_width=True,
        height=280
    )
    
    render_export_button(cleared_pts, "discharged_eligible_cohort.csv")
