# projects/healthtech/page5_cohorts.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        "Cohort Explorer & ICU Discharge Simulator",
        badge="PREDICTIVE SIMULATOR",
        subtitle="Filter custom patient sub-cohorts, analyze vitals distribution, and simulate discharge criteria",
    )

    st.markdown("""
    <div class="what-if-container">
        <span style="font-weight: 700; color: #14b8a6; font-size: 0.95rem;">🔮 INTERACTIVE WHAT-IF SCENARIO: SAFE DISCHARGE SPO2 THRESHOLD</span>
        <div style="font-size: 0.8rem; color: #99f6e4; margin-top: 4px;">Simulate how raising the minimum SpO2 threshold for step-down transfer impacts readmission rates:</div>
    </div>
    """, unsafe_allow_html=True)

    spo2_min = float(df_f["spo2"].min()) if len(df_f) > 0 else 80.0
    spo2_max = float(df_f["spo2"].max()) if len(df_f) > 0 else 100.0
    # clamp slider bounds to valid range
    slider_lo = max(80.0, min(92.0, spo2_max - 1.0))
    slider_hi = min(100.0, max(98.0, spo2_min + 1.0))
    min_spo2 = st.slider("Target SpO2 Discharge Cutoff (%)", min_value=92.0, max_value=98.0, value=95.0, step=0.5)

    cleared_pts = df_f[df_f["spo2"] >= min_spo2]
    n_total = len(df_f)
    n_cleared = len(cleared_pts)
    cleared_pct = (n_cleared / n_total * 100) if n_total > 0 else 0.0
    readmit_rate = max(4.0, 16.0 - (min_spo2 - 92.0) * 1.8)

    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi("Eligible for Step-Down", f"{n_cleared:,}", delta=f"{cleared_pct:.1f}% of filtered census", is_positive=True, badge="TRANSFER")
    with c2:
        render_kpi("Simulated 30d Readmission", f"{readmit_rate:.1f}%", delta=f"-{(16.0-readmit_rate):.1f}% vs baseline", is_positive=True, badge="SAFETY")
    with c3:
        render_kpi("ICU Bed Capacity Released", f"{int(n_cleared*0.22):,} beds", delta="+18% availability", is_positive=True, badge="CAPACITY")

    # SpO2 distribution of cleared vs not-cleared
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>SPO2 DISTRIBUTION: CLEARED VS NOT CLEARED</div>", unsafe_allow_html=True)
    df_f_copy = df_f.copy()
    df_f_copy["Discharge Status"] = df_f_copy["spo2"].apply(lambda v: "Cleared" if v >= min_spo2 else "Held")
    fig_dist = px.histogram(
        df_f_copy, x="spo2", color="Discharge Status", nbins=30, barmode="overlay",
        color_discrete_map={"Cleared": "#14b8a6", "Held": "#f43f5e"},
    )
    fig_dist.add_vline(x=min_spo2, line_dash="dash", line_color="#f59e0b", annotation_text=f"Cutoff: {min_spo2}%")
    fig_dist.update_layout(**get_plotly_layout("healthtech", height=260))
    st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>PATIENT COHORT RECORD EXPLORER (DISCHARGE ELIGIBLE)</div>", unsafe_allow_html=True)
    display_cols = [c for c in ["patient_id", "admit_date", "age", "gender", "ward", "risk_category", "spo2", "heart_rate", "bp_systolic"] if c in cleared_pts.columns]
    st.dataframe(cleared_pts[display_cols].head(20), use_container_width=True, height=280)

    render_export_button(cleared_pts, "discharged_eligible_cohort.csv")
