# projects/saas/page5_forecast.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    # ── Sidebar filters ──────────────────────────────────────────────────────
    with st.sidebar:
        with st.expander("🔍 FILTERS", expanded=True):
            tiers = st.multiselect(
                "Subscription Tier",
                options=df["tier"].unique().tolist(),
                default=df["tier"].unique().tolist(),
            )
            channels = st.multiselect(
                "Acquisition Channel",
                options=df["channel"].unique().tolist(),
                default=df["channel"].unique().tolist(),
            )
            churned_filter = st.radio(
                "Customer Status",
                ["All", "Active Only", "Churned Only"],
                index=0,
            )

    # ── Apply filters ────────────────────────────────────────────────────────
    df_f = df[df["tier"].isin(tiers) & df["channel"].isin(channels)]
    if churned_filter == "Active Only":
        df_f = df_f[~df_f["churned"]]
    elif churned_filter == "Churned Only":
        df_f = df_f[df_f["churned"]]

    render_section_header(
        "Scenario Forecasting & Churn Reduction Simulator",
        badge="PREDICTIVE",
        subtitle="Interactive simulation modeling compound ARR trajectory under varying churn & expansion parameters",
    )

    st.markdown("""
    <div class="what-if-container">
        <span style="font-weight: 700; color: #8b5cf6; font-size: 0.95rem;">🔮 INTERACTIVE WHAT-IF SCENARIO: CHURN REDUCTION LEVERAGE</span>
        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">Simulate how improving customer retention compounds annual recurring revenue over the next 24 months:</div>
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        churn_reduction_pct = st.slider("Monthly Churn Improvement (-%)", min_value=0.0, max_value=4.0, value=1.5, step=0.1)
    with col_s2:
        expansion_boost_pct = st.slider("Net Expansion Boost (+%)", min_value=0.0, max_value=5.0, value=2.0, step=0.2)

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
        render_kpi("Retention Compounding Delta", f"+{(opt_proj[-1] / base_proj[-1] - 1) * 100:.1f}%", is_positive=True, subtext="Compounded over 24 months", badge="LEVERAGE")

    # ── Forecast chart with confidence band ─────────────────────────────────
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

    fig_proj.update_layout(**get_plotly_layout("saas", height=340))
    st.plotly_chart(fig_proj, use_container_width=True)

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
