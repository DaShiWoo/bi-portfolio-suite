# projects/healthtech/page2_vitals.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Vitals Density & Cardiovascular Biomarkers", badge="BIOMETRICS", subtitle="High-density statistical distributions of systolic blood pressure, heart rate, and oxygenation")
    
    mean_bp = df["bp_systolic"].mean()
    mean_hr = df["heart_rate"].mean()
    hypoxia = len(df[df["spo2"] < 90])
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Mean Systolic BP", f"{mean_bp:.0f} mmHg", delta="+2.4 mmHg", is_positive=False, badge="BLOOD PRESSURE")
    with c2:
        render_kpi("Mean Resting HR", f"{mean_hr:.0f} bpm", delta="Normal resting range", is_positive=True, badge="HEART RATE")
    with c3:
        render_kpi("Acute Hypoxia Events", f"{hypoxia} cases", delta="SpO2 < 90% threshold", is_positive=False, badge="HYPOXIA")
    with c4:
        render_kpi("Cardio Correlation", "r = 0.68", delta="Strong BP to HR link", is_positive=True, badge="CORRELATION")
        
    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>SYSTOLIC BLOOD PRESSURE DENSITY</div>", unsafe_allow_html=True)
        fig_bp = px.histogram(df, x="bp_systolic", color="risk_category", nbins=30, barmode="overlay", color_discrete_sequence=["#14b8a6", "#38bdf8", "#f59e0b", "#f43f5e"])
        fig_bp.update_layout(**get_plotly_layout("healthtech", height=300))
        st.plotly_chart(fig_bp, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>HEART RATE VS SPO2 SCATTER MAP</div>", unsafe_allow_html=True)
        sample = df.sample(min(800, len(df)))
        fig_sc = px.scatter(sample, x="heart_rate", y="spo2", color="risk_category", hover_data=["patient_id", "ward"], color_discrete_sequence=["#14b8a6", "#38bdf8", "#f59e0b", "#f43f5e"])
        fig_sc.update_layout(**get_plotly_layout("healthtech", height=300))
        st.plotly_chart(fig_sc, use_container_width=True)
        
    render_export_button(df[["patient_id", "age", "heart_rate", "hrv_ms", "spo2", "bp_systolic"]], "vitals_density_metrics.csv")
