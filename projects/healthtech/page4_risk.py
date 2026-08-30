# projects/healthtech/page4_risk.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout
from core.filters import build_healthtech_filters, check_empty_state


def render(df: pd.DataFrame) -> None:
    """Render the Patient Risk Stratification & Early Decompensation page."""
    df_f = build_healthtech_filters(df, key_prefix="health_p4")
    if check_empty_state(df_f, "patients"):
        return

    render_section_header(
        "Patient Risk Stratification & Early Decompensation",
        badge="RISK ENGINE",
        subtitle="Predictive risk scoring models for early identification of acute clinical deterioration",
    )

    n = len(df_f)
    crit_df = df_f[df_f["risk_category"] == "Critical Alert"]
    high_df = df_f[df_f["risk_category"] == "High Risk"]
    at_risk_pct = ((len(crit_df) + len(high_df)) / n * 100) if n > 0 else 0.0
    geriatric = len(df_f[df_f["age"] > 70])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("High & Critical Acuity", f"{len(crit_df)+len(high_df):,}", delta=f"{at_risk_pct:.1f}% of filtered census", is_positive=False, badge="AT RISK")
    with c2:
        render_kpi("Early Warning Score (EWS)", "3.4 / 10", delta="Normalized risk index", is_positive=True, badge="EWS")
    with c3:
        render_kpi("Decompensation Lead Time", "4.8 hrs", delta="+1.2 hrs earlier", is_positive=True, subtext="Time to intervene prior to shock", badge="LEAD TIME")
    with c4:
        render_kpi("Geriatric Cohort (>70yo)", f"{geriatric:,}", delta=f"{(geriatric/n*100):.1f}% of cohort" if n > 0 else "0%", is_positive=False, badge="GERIATRIC")

    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>AGE BRACKET VS RISK CATEGORY</div>", unsafe_allow_html=True)
        df_f_copy = df_f.copy()
        df_f_copy["age_bracket"] = pd.cut(df_f_copy["age"], bins=[18, 40, 60, 75, 100], labels=["18-39", "40-59", "60-74", "75+"])
        age_risk = df_f_copy.groupby(["age_bracket", "risk_category"], observed=True).size().reset_index(name="Count")
        fig_ar = px.bar(
            age_risk, x="age_bracket", y="Count", color="risk_category", barmode="stack",
            color_discrete_map={"Low Risk": "#14b8a6", "Moderate": "#38bdf8", "High Risk": "#f59e0b", "Critical Alert": "#f43f5e"},
        )
        fig_ar.update_layout(**get_plotly_layout("healthtech", height=300))
        st.plotly_chart(fig_ar, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #99f6e4; margin-bottom: 8px;'>WARD-LEVEL CRITICAL PATIENT %</div>", unsafe_allow_html=True)
        ward_risk = (
            df_f.groupby("ward")["risk_category"]
            .apply(lambda x: (x == "Critical Alert").mean() * 100)
            .reset_index(name="Crit_Pct")
        )
        fig_wr = px.bar(
            ward_risk, x="ward", y="Crit_Pct", color="Crit_Pct",
            color_continuous_scale=["#14b8a6", "#f43f5e"],
            labels={"Crit_Pct": "Critical %", "ward": "Ward"},
        )
        fig_wr.update_layout(**get_plotly_layout("healthtech", height=300), coloraxis_showscale=False)
        st.plotly_chart(fig_wr, use_container_width=True)

    render_export_button(crit_df[["patient_id", "age", "ward", "heart_rate", "spo2", "bp_systolic"]], "critical_alerts_cohort.csv")
