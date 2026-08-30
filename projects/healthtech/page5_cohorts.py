# projects/healthtech/page5_cohorts.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout
from core.filters import build_healthtech_filters, check_empty_state


def render(df: pd.DataFrame) -> None:
    """Render the Cohort Explorer & ICU Discharge Simulator page."""
    df_f = build_healthtech_filters(df, key_prefix="health_p5")
    if check_empty_state(df_f, "patients"):
        return

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

    df_f_copy = df_f.copy()
    df_f_copy["Discharge Status"] = df_f_copy["spo2"].apply(lambda v: "Cleared" if v >= min_spo2 else "Held")

    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>SPO2 DISTRIBUTION: CLEARED VS NOT CLEARED</div>", unsafe_allow_html=True)
        fig_dist = px.histogram(
            df_f_copy, x="spo2", color="Discharge Status", nbins=30, barmode="overlay",
            color_discrete_map={"Cleared": "#14b8a6", "Held": "#f43f5e"},
        )
        fig_dist.add_vline(x=min_spo2, line_dash="dash", line_color="#f59e0b", annotation_text=f"Cutoff: {min_spo2}%")
        fig_dist.update_layout(**get_plotly_layout("healthtech", height=280))
        st.plotly_chart(fig_dist, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>DISCHARGE ELIGIBILITY BY WARD</div>", unsafe_allow_html=True)
        ward_status = df_f_copy.groupby(["ward", "Discharge Status"], observed=True).size().reset_index(name="Count")
        fig_ws = px.bar(
            ward_status, x="ward", y="Count", color="Discharge Status", barmode="stack",
            color_discrete_map={"Cleared": "#14b8a6", "Held": "#f43f5e"},
        )
        fig_ws.update_layout(**get_plotly_layout("healthtech", height=280))
        st.plotly_chart(fig_ws, use_container_width=True)

    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>PATIENT COHORT RECORD EXPLORER (DISCHARGE ELIGIBLE)</div>", unsafe_allow_html=True)
    display_cols = [c for c in ["patient_id", "admit_date", "age", "gender", "ward", "risk_category", "spo2", "heart_rate", "bp_systolic"] if c in cleared_pts.columns]
    st.dataframe(cleared_pts[display_cols].head(20), use_container_width=True, height=280)

    render_export_button(cleared_pts, "discharged_eligible_cohort.csv")
