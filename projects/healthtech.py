"""
projects/healthtech.py
HealthTech & Patient Biometrics Clinical Telemetry Dashboard.
Design: Dark Teal & Mint Clinical (Frosted glass, hospital command center).
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, get_plotly_layout

def render():
    df = pd.read_parquet("data/health_telemetry.parquet")
    
    total_patients = len(df)
    critical_alerts = len(df[df["risk_category"] == "Critical Alert"])
    avg_hrv = df["hrv_ms"].mean()
    mean_spo2 = df["spo2_percent"].mean()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Monitored Patients", f"{total_patients:,}", delta="+42 active admissions", is_positive=True, subtext="Telemetry live feed", badge="ICU/WARD")
    with c2:
        render_kpi("Critical Vitals Alerts", f"{critical_alerts}", delta="-5 resolved", is_positive=True, subtext="Immediate intervention trigger", badge="ALERTS")
    with c3:
        render_kpi("Cohort Mean SpO2", f"{mean_spo2:.1f}%", delta="+0.4%", is_positive=True, subtext="Standard threshold > 95%", badge="OXYGEN")
    with c4:
        render_kpi("Mean Heart Rate Var.", f"{avg_hrv:.1f} ms", delta="+3.2 ms", is_positive=True, subtext="Cardiovascular resilience", badge="HRV")
        
    render_section_header("Clinical Survival Curves & Cohort Risk Distribution", badge="PREDICTIVE AI")
    c_mid1, c_mid2 = st.columns([7, 5])
    
    with c_mid1:
        # Kaplan-Meier survival curves for Treatment A vs B
        timeline = np.linspace(0, 36, 50)
        surv_ai = np.exp(-timeline / 26) * 100
        surv_std = np.exp(-timeline / 18) * 100
        
        fig_km = go.Figure()
        fig_km.add_trace(go.Scatter(
            x=timeline, y=surv_ai, name="AI Predictive Protocol",
            line=dict(color="#14b8a6", width=3)
        ))
        fig_km.add_trace(go.Scatter(
            x=timeline, y=surv_std, name="Standard Care Protocol",
            line=dict(color="#f43f5e", width=2.5, dash="dash")
        ))
        fig_km.update_layout(**get_plotly_layout("healthtech", height=330))
        st.plotly_chart(fig_km, use_container_width=True)
        
    with c_mid2:
        # Risk Category distribution donut
        risk_agg = df["risk_category"].value_counts().reset_index()
        risk_agg.columns = ["Risk", "Patients"]
        fig_donut = px.pie(
            risk_agg, values="Patients", names="Risk", hole=0.6,
            color="Risk", color_discrete_map={
                "Low Risk": "#14b8a6", "Moderate": "#38bdf8",
                "High Risk": "#f59e0b", "Critical Alert": "#f43f5e"
            }
        )
        fig_donut.update_layout(**get_plotly_layout("healthtech", height=330))
        st.plotly_chart(fig_donut, use_container_width=True)
        
    render_section_header("Vitals Density & Telemetry Patient Table", badge="TELEMETRY FEED")
    c_bot1, c_bot2 = st.columns([6, 6])
    
    with c_bot1:
        # Heart rate distribution by risk category
        fig_hist = px.histogram(
            df, x="heart_rate_bpm", color="risk_category", barmode="overlay",
            nbins=35, color_discrete_sequence=["#14b8a6", "#38bdf8", "#f59e0b", "#f43f5e"]
        )
        fig_hist.update_layout(**get_plotly_layout("healthtech", height=290))
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with c_bot2:
        st.dataframe(
            df[["patient_id", "age", "gender", "risk_category", "heart_rate_bpm", "hrv_ms", "spo2_percent"]].head(15),
            use_container_width=True,
            height=290
        )
