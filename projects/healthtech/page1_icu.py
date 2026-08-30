# projects/healthtech/page1_icu.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    # ── Sidebar Filters ───────────────────────────────────────────────────────
    with st.sidebar:
        with st.expander("🔍 FILTERS", expanded=True):
            wards = st.multiselect(
                "Clinical Ward",
                options=df["ward"].unique().tolist(),
                default=df["ward"].unique().tolist(),
            )
            risk_cats = st.multiselect(
                "Risk Category",
                options=df["risk_category"].unique().tolist(),
                default=df["risk_category"].unique().tolist(),
            )
            age_range = st.slider(
                "Patient Age Range",
                int(df["age"].min()), int(df["age"].max()),
                (int(df["age"].min()), int(df["age"].max())),
            )

    df_f = df[
        df["ward"].isin(wards) &
        df["risk_category"].isin(risk_cats) &
        (df["age"] >= age_range[0]) &
        (df["age"] <= age_range[1])
    ]

    render_section_header(
        "Clinical ICU Telemetry & Real-Time Vitals",
        badge="HOSPITAL COMMAND",
        subtitle="Continuous patient vital sign monitoring, acute alert notifications, and ward occupancy",
    )

    total_pts = len(df_f)
    critical_alerts = len(df_f[df_f["risk_category"] == "Critical Alert"])
    mean_spo2 = df_f["spo2"].mean() if total_pts > 0 else 0.0
    mean_hrv = df_f["hrv_ms"].mean() if total_pts > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Monitored Inpatients", f"{total_pts:,}", delta="+18 admissions today", is_positive=True, badge="CENSUS")
    with c2:
        crit_pct = (critical_alerts / total_pts * 100) if total_pts > 0 else 0.0
        render_kpi("Critical Vitals Alerts", f"{critical_alerts}", delta=f"{crit_pct:.1f}% of cohort", is_positive=False, subtext="Requires immediate intervention", badge="ALERTS")
    with c3:
        render_kpi("Cohort Mean SpO2", f"{mean_spo2:.1f}%", delta="Normal range > 95%", is_positive=mean_spo2 >= 95, badge="OXYGEN")
    with c4:
        render_kpi("Cardiovascular HRV", f"{mean_hrv:.1f} ms", delta="+2.8 ms resilience", is_positive=True, badge="HRV")

    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>PATIENT DISTRIBUTION ACROSS CLINICAL WARDS</div>", unsafe_allow_html=True)
        ward_agg = df_f.groupby("ward").agg(
            Patients=("patient_id", "count"),
            Critical=("risk_category", lambda x: (x == "Critical Alert").sum()),
        ).reset_index()
        fig_w = px.bar(ward_agg, x="ward", y=["Patients", "Critical"], barmode="group", color_discrete_sequence=["#14b8a6", "#f43f5e"])
        fig_w.update_layout(**get_plotly_layout("healthtech", height=300))
        st.plotly_chart(fig_w, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>ACUITY RISK STRATIFICATION</div>", unsafe_allow_html=True)
        risk_cnt = df_f["risk_category"].value_counts().reset_index()
        risk_cnt.columns = ["Risk", "Count"]
        fig_r = px.pie(
            risk_cnt, values="Count", names="Risk", hole=0.6, color="Risk",
            color_discrete_map={"Low Risk": "#14b8a6", "Moderate": "#38bdf8", "High Risk": "#f59e0b", "Critical Alert": "#f43f5e"},
        )
        fig_r.update_layout(**get_plotly_layout("healthtech", height=300))
        st.plotly_chart(fig_r, use_container_width=True)

    render_export_button(df_f[["patient_id", "ward", "risk_category", "heart_rate", "spo2", "bp_systolic"]].head(500), "icu_vitals_telemetry.csv")
