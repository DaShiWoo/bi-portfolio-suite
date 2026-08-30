# projects/saas/page5_forecast.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from core.filters import build_saas_filters, check_empty_state
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout


def render(df: pd.DataFrame) -> None:
    """Render interactive scenario forecasting and churn reduction simulator dashboard."""
    render_section_header(
        "Scenario Forecasting & Churn Reduction Simulator",
        badge="PREDICTIVE",
        subtitle="Interactive simulation modeling compound ARR trajectory under varying churn & expansion parameters",
    )

    df_f = build_saas_filters(df, key_prefix="saas_p5")
    if check_empty_state(df_f, "subscribers"):
        return

    st.markdown("""
    <div class="what-if-container">
        <span style="font-weight: 700; color: #8b5cf6; font-size: 0.95rem;">🔮 INTERACTIVE WHAT-IF SCENARIO: CHURN REDUCTION LEVERAGE</span>
        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">Simulate how improving customer retention compounds annual recurring revenue over the next 24 months:</div>
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        churn_reduction_pct = st.slider("Monthly Churn Improvement (-%)", min_value=0.0, max_value=4.0, value=1.5, step=0.1, key="saas_p5_churn_slider")
    with col_s2:
        expansion_boost_pct = st.slider("Net Expansion Boost (+%)", min_value=0.0, max_value=5.0, value=2.0, step=0.2, key="saas_p5_exp_slider")

    current_mrr = df_f["mrr"].sum()
    months_ahead = 24

    # ── Simulate trajectories + confidence band ──────────────────────────────
    np.random.seed(42)
    base_proj, opt_proj, opt_upper, opt_lower = [], [], [], []
    curr_base = current_mrr
    curr_opt = current_mrr

    for i in range(months_ahead):
        curr_base = curr_base * (1 + 0.025 - 0.015)
        growth_rate = 0.025 + (expansion_boost_pct / 100) - (0.015 - (churn_reduction_pct / 100))
        curr_opt = curr_opt * (1 + growth_rate)
        noise = np.random.normal(0, curr_opt * 0.018)
        base_proj.append(curr_base)
        opt_proj.append(curr_opt)
        opt_upper.append(curr_opt + abs(noise) * (1 + i * 0.05))
        opt_lower.append(max(0, curr_opt - abs(noise) * (1 + i * 0.05)))

    delta_arr = (opt_proj[-1] - base_proj[-1]) * 12

    # ── KPIs ─────────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi("Current Baseline ARR", f"${current_mrr * 12:,.0f}", badge="CURRENT")
    with c2:
        render_kpi("Optimized 24M ARR Target", f"${opt_proj[-1] * 12:,.0f}", delta=f"+${delta_arr:,.0f} ARR Lift", is_positive=True, badge="FORECAST")
    with c3:
        render_kpi("Retention Compounding Delta", f"+{(opt_proj[-1] / base_proj[-1] - 1) * 100:.1f}%" if base_proj[-1] > 0 else "0.0%", is_positive=True, subtext="Compounded over 24 months", badge="LEVERAGE")

    # ── Chart 1: Forecast chart with confidence band ─────────────────────────
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>24-MONTH ARR PROJECTION WITH CONFIDENCE BAND</div>", unsafe_allow_html=True)
    months_labels = [f"M+{i + 1}" for i in range(months_ahead)]

    fig_proj = go.Figure()

    # Upper bound (invisible, for fill reference)
    fig_proj.add_trace(go.Scatter(
        x=months_labels, y=[u * 12 for u in opt_upper],
        mode="lines", line=dict(width=0), showlegend=False, name="Upper",
    ))
    # Lower bound with fill to upper
    fig_proj.add_trace(go.Scatter(
        x=months_labels, y=[l * 12 for l in opt_lower],
        mode="lines", line=dict(width=0),
        fill="tonexty", fillcolor="rgba(139,92,246,0.15)",
        name="Confidence Band", showlegend=True,
    ))
    # Baseline
    fig_proj.add_trace(go.Scatter(
        x=months_labels, y=[b * 12 for b in base_proj],
        name="Status Quo Baseline",
        line=dict(color="rgba(148,163,184,0.6)", width=2, dash="dash"),
    ))
    # Optimized trajectory
    fig_proj.add_trace(go.Scatter(
        x=months_labels, y=[o * 12 for o in opt_proj],
        name="Optimized Trajectory",
        line=dict(color="#8b5cf6", width=3),
    ))

    fig_proj.update_layout(**get_plotly_layout("saas", height=320))
    st.plotly_chart(fig_proj, use_container_width=True)

    # ── Chart 2: Milestone ARR Comparison Bar Chart ──────────────────────────
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin: 12px 0 8px;'>MILESTONE ARR COMPARISON (STATUS QUO VS OPTIMIZED)</div>", unsafe_allow_html=True)
    milestones = [5, 11, 17, 23]
    milestone_labels = ["6 Months", "12 Months", "18 Months", "24 Months"]
    ms_df = pd.DataFrame({
        "Milestone": milestone_labels,
        "Status Quo Baseline": [base_proj[m] * 12 for m in milestones],
        "Optimized Trajectory": [opt_proj[m] * 12 for m in milestones],
    })
    fig_ms = px.bar(
        ms_df, x="Milestone", y=["Status Quo Baseline", "Optimized Trajectory"],
        barmode="group",
        color_discrete_sequence=["rgba(148,163,184,0.6)", "#8b5cf6"],
        labels={"value": "Projected ARR ($)", "variable": "Scenario"},
    )
    fig_ms.update_layout(**get_plotly_layout("saas", height=280))
    st.plotly_chart(fig_ms, use_container_width=True)

    render_export_button(
        pd.DataFrame({
            "Month": months_labels,
            "Baseline_ARR": [b * 12 for b in base_proj],
            "Optimized_ARR": [o * 12 for o in opt_proj],
            "Upper_95": [u * 12 for u in opt_upper],
            "Lower_95": [l * 12 for l in opt_lower],
        }),
        "arr_scenario_projection.csv",
    )
