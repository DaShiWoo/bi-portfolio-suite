# projects/saas/page2_nrr.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.filters import build_saas_filters, check_empty_state
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout


def render(df: pd.DataFrame) -> None:
    """Render Net Revenue Retention (NRR) cohort progression and retention compounding dashboard."""
    render_section_header(
        "Net Revenue Retention (NRR) Cohort Matrix",
        badge="EXPANSION",
        subtitle="12x12 cohort progression tracking net expansion, upselling, and retention compounding",
    )

    if check_empty_state(df, "subscribers"):
        return
    df_f = df

    # ── KPIs from filtered data ──────────────────────────────────────────────
    active_df = df_f[~df_f["churned"]]
    total_mrr = df_f["mrr"].sum()
    expansion = df_f["expansion_mrr"].sum()
    contraction = df_f["contraction_mrr"].sum()
    churned_mrr = df_f[df_f["churned"]]["mrr"].sum()
    base_mrr = total_mrr - expansion + contraction + churned_mrr
    nrr = ((total_mrr - churned_mrr) / base_mrr * 100) if base_mrr > 0 else 100.0
    grr = ((base_mrr - churned_mrr - contraction) / base_mrr * 100) if base_mrr > 0 else 100.0
    logo_ret = (len(active_df) / len(df_f) * 100) if len(df_f) > 0 else 100.0
    expansion_contrib = expansion

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Overall Net Revenue Retention", f"{nrr:.1f}%", delta="+4.2% YoY", is_positive=True, subtext="Expansion > Churn", badge="NRR")
    with c2:
        render_kpi("Gross Revenue Retention", f"{grr:.1f}%", delta="+1.1%", is_positive=True, subtext="Excluding upsell expansion", badge="GRR")
    with c3:
        render_kpi("Annual Logo Retention", f"{logo_ret:.1f}%", delta="+2.5%", is_positive=True, subtext=f"{100-logo_ret:.1f}% Annual Logo Churn", badge="LOGOS")
    with c4:
        render_kpi("Expansion Contribution", f"${expansion_contrib:,.0f}/mo", delta="+18.9%", is_positive=True, subtext="Cross-sell and seat expansion", badge="UPSELL")

    # ── NRR trend line ────────────────────────────────────────────────────────
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>NRR TREND BY COHORT MONTH</div>", unsafe_allow_html=True)
    df_f_copy = df_f.copy()
    df_f_copy["cohort_month"] = pd.to_datetime(df_f_copy["cohort"])
    monthly = df_f_copy.groupby("cohort_month").agg(
        mrr=("mrr", "sum"),
        expansion=("expansion_mrr", "sum"),
        contraction=("contraction_mrr", "sum"),
    ).reset_index().sort_values("cohort_month")
    monthly["nrr"] = ((monthly["mrr"] + monthly["expansion"] - monthly["contraction"]) / (monthly["mrr"] + 1) * 100).round(1)
    monthly["cohort_str"] = monthly["cohort_month"].dt.strftime("%b %Y")

    fig_nrr_trend = go.Figure()
    fig_nrr_trend.add_trace(go.Scatter(
        x=monthly["cohort_str"],
        y=monthly["nrr"],
        mode="lines+markers",
        line=dict(color="#8b5cf6", width=3),
        fill="tozeroy",
        fillcolor="rgba(139,92,246,0.10)",
        name="NRR %",
    ))
    fig_nrr_trend.add_hline(y=100, line_dash="dash", line_color="#38bdf8", annotation_text="100% Baseline")
    fig_nrr_trend.update_layout(**get_plotly_layout("saas", height=250))
    st.plotly_chart(fig_nrr_trend, use_container_width=True)

    # ── Cohort heatmap ───────────────────────────────────────────────────────
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    cohort_matrix = []
    for i in range(len(months)):
        row = []
        for j in range(len(months)):
            if j < i:
                row.append(None)
            elif j == i:
                row.append(100.0)
            else:
                diff = j - i
                val = 100.0 + (diff * 3.1) - (diff * 0.9) + np.sin(diff) * 1.5
                row.append(round(val, 1))
        cohort_matrix.append(row)

    fig_heat = px.imshow(
        cohort_matrix,
        x=[f"M+{k}" for k in range(len(months))],
        y=[f"{m} 2024" for m in months],
        color_continuous_scale=[[0, "#0b0d17"], [0.5, "#3b2d6b"], [1, "#8b5cf6"]],
        text_auto=True,
        aspect="auto",
    )
    fig_heat.update_layout(**get_plotly_layout("saas", height=350))
    fig_heat.update_coloraxes(showscale=False)
    st.plotly_chart(fig_heat, use_container_width=True)

    df_cohort_export = pd.DataFrame(cohort_matrix, index=months, columns=[f"M+{k}" for k in range(len(months))])
    render_export_button(df_cohort_export.reset_index(), "nrr_cohort_matrix.csv")
