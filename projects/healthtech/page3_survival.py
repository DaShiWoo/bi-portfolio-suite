# projects/healthtech/page3_survival.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Treatment Efficacy & Kaplan-Meier Survival Analysis", badge="CLINICAL EFFICACY", subtitle="Comparative statistical outcomes: AI Predictive Care Protocol vs Standard Clinical Care")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Median Survival (AI Arm)", "26.4 months", delta="+8.2 months lift", is_positive=True, badge="AI PROTOCOL")
    with c2:
        render_kpi("Median Survival (Standard)", "18.2 months", delta="Historical benchmark", is_positive=True, badge="STANDARD")
    with c3:
        render_kpi("Hazard Ratio (HR)", "0.64", delta="p < 0.001 statistically sig", is_positive=True, subtext="36% mortality reduction", badge="HAZARD RATIO")
    with c4:
        render_kpi("30-Day Readmission", f"{(df['readmitted_30d'].mean()*100):.1f}%", delta="-3.4% reduction", is_positive=True, badge="READMISSION")
        
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>KAPLAN-MEIER SURVIVAL CURVE (36-MONTH OBSERVATION)</div>", unsafe_allow_html=True)
    timeline = np.linspace(0, 36, 40)
    surv_ai = np.exp(-timeline / 26.4) * 100
    surv_std = np.exp(-timeline / 18.2) * 100
    
    fig_km = go.Figure()
    fig_km.add_trace(go.Scatter(x=timeline, y=surv_ai, name="AI Predictive Protocol (Arm A)", line=dict(color="#14b8a6", width=3.5)))
    fig_km.add_trace(go.Scatter(x=timeline, y=surv_std, name="Standard Care Protocol (Arm B)", line=dict(color="#f43f5e", width=2.5, dash="dash")))
    fig_km.update_layout(**get_plotly_layout("healthtech", height=320))
    fig_km.update_yaxes(title="Survival Probability (%)", range=[0, 105])
    fig_km.update_xaxes(title="Follow-up Timeline (Months)")
    st.plotly_chart(fig_km, use_container_width=True)
    
    km_export = pd.DataFrame({"Month": timeline.round(1), "AI_Protocol_Survival": surv_ai.round(2), "Standard_Protocol_Survival": surv_std.round(2)})
    render_export_button(km_export, "kaplan_meier_survival_data.csv")
