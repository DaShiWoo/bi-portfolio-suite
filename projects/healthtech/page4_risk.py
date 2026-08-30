# projects/healthtech/page4_risk.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Patient Risk Stratification & Early Decompensation", badge="RISK ENGINE", subtitle="Predictive risk scoring models for early identification of acute clinical deterioration")
    
    crit_df = df[df["risk_category"] == "Critical Alert"]
    high_df = df[df["risk_category"] == "High Risk"]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("High & Critical Acuity", f"{len(crit_df)+len(high_df):,}", delta="24% of inpatient census", is_positive=False, badge="AT RISK")
    with c2:
        render_kpi("Early Warning Score (EWS)", "3.4 / 10", delta="Normalized risk index", is_positive=True, badge="EWS")
    with c3:
        render_kpi("Decompensation Lead Time", "4.8 hrs", delta="+1.2 hrs earlier", is_positive=True, subtext="Time to intervene prior to shock", badge="LEAD TIME")
    with c4:
        render_kpi("Geriatric Cohort (>70yo)", f"{len(df[df['age']>70]):,}", delta="Vulnerable subgroup", is_positive=False, badge="GERIATRIC")
        
    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>AGE BRACKET VS RISK CATEGORY</div>", unsafe_allow_html=True)
        df["age_bracket"] = pd.cut(df["age"], bins=[18, 40, 60, 75, 100], labels=["18-39", "40-59", "60-74", "75+"])
        age_risk = df.groupby(["age_bracket", "risk_category"]).size().reset_index(name="Count")
        fig_ar = px.bar(age_risk, x="age_bracket", y="Count", color="risk_category", barmode="stack", color_discrete_sequence=["#14b8a6", "#38bdf8", "#f59e0b", "#f43f5e"])
        fig_ar.update_layout(**get_plotly_layout("healthtech", height=300))
        st.plotly_chart(fig_ar, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>WARD-LEVEL RISK CONCENTRATION</div>", unsafe_allow_html=True)
        ward_risk = df.groupby("ward")["risk_category"].apply(lambda x: (x=="Critical Alert").mean()*100).reset_index(name="Crit_Pct")
        fig_wr = px.bar(ward_risk, x="ward", y="Crit_Pct", color="Crit_Pct", color_continuous_scale=["#14b8a6", "#f43f5e"])
        fig_wr.update_layout(**get_plotly_layout("healthtech", height=300), coloraxis_showscale=False)
        st.plotly_chart(fig_wr, use_container_width=True)
        
    render_export_button(crit_df[["patient_id", "age", "ward", "heart_rate", "spo2", "bp_systolic"]], "critical_alerts_cohort.csv")
