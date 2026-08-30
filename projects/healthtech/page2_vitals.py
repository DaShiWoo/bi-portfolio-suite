# projects/healthtech/page2_vitals.py
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
        "Vitals Density & Cardiovascular Biomarkers",
        badge="BIOMETRICS",
        subtitle="High-density statistical distributions of systolic blood pressure, heart rate, and oxygenation",
    )

    n = len(df_f)
    mean_bp = df_f["bp_systolic"].mean() if n > 0 else 0.0
    mean_hr = df_f["heart_rate"].mean() if n > 0 else 0.0
    hypoxia = len(df_f[df_f["spo2"] < 90])
    hyper = len(df_f[df_f["bp_systolic"] > 140])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Mean Systolic BP", f"{mean_bp:.0f} mmHg", delta="+2.4 mmHg", is_positive=False, badge="BLOOD PRESSURE")
    with c2:
        render_kpi("Mean Resting HR", f"{mean_hr:.0f} bpm", delta="Normal resting range", is_positive=True, badge="HEART RATE")
    with c3:
        render_kpi("Acute Hypoxia Events", f"{hypoxia} cases", delta="SpO2 < 90% threshold", is_positive=False, badge="HYPOXIA")
    with c4:
        render_kpi("Hypertension Cases", f"{hyper}", delta="BP Systolic > 140 mmHg", is_positive=False, badge="HYPERTENSION")

    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>SYSTOLIC BLOOD PRESSURE DENSITY</div>", unsafe_allow_html=True)
        fig_bp = px.histogram(
            df_f, x="bp_systolic", color="risk_category", nbins=30, barmode="overlay",
            color_discrete_map={"Low Risk": "#14b8a6", "Moderate": "#38bdf8", "High Risk": "#f59e0b", "Critical Alert": "#f43f5e"},
        )
        fig_bp.update_layout(**get_plotly_layout("healthtech", height=300))
        st.plotly_chart(fig_bp, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>HEART RATE VS SPO2 SCATTER MAP</div>", unsafe_allow_html=True)
        sample = df_f.sample(min(800, len(df_f)), random_state=42) if n > 0 else df_f
        fig_sc = px.scatter(
            sample, x="heart_rate", y="spo2", color="risk_category",
            hover_data=["patient_id", "ward"],
            color_discrete_map={"Low Risk": "#14b8a6", "Moderate": "#38bdf8", "High Risk": "#f59e0b", "Critical Alert": "#f43f5e"},
        )
        fig_sc.update_layout(**get_plotly_layout("healthtech", height=300))
        st.plotly_chart(fig_sc, use_container_width=True)

    render_export_button(df_f[["patient_id", "age", "heart_rate", "hrv_ms", "spo2", "bp_systolic"]], "vitals_density_metrics.csv")
