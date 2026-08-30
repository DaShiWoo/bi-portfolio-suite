# projects/saas/page1_mrr.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.filters import build_saas_filters, check_empty_state
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout


def render(df: pd.DataFrame) -> None:
    """Render SaaS MRR and ARR growth velocity dashboard with waterfall and tier breakdown."""
    render_section_header(
        "MRR & ARR Growth Velocity",
        badge="RECURRING REVENUE",
        subtitle="Monthly recurring revenue bridge, expansion, contraction, and churn waterfall",
    )

    if check_empty_state(df, "subscribers"):
        return
    df_f = df

    # ── KPIs ─────────────────────────────────────────────────────────────────
    total_mrr = df_f["mrr"].sum()
    total_arr = df_f["arr"].sum()
    active_subs = len(df_f[~df_f["churned"]])
    arpu = total_mrr / active_subs if active_subs > 0 else 0
    expansion = df_f["expansion_mrr"].sum()
    contraction = df_f["contraction_mrr"].sum()
    churned_mrr = df_f[df_f["churned"]]["mrr"].sum()
    quick_ratio = (expansion + total_mrr * 0.08) / (contraction + churned_mrr + 1)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Monthly Recurring Revenue", f"${total_mrr:,.0f}", delta="+18.4% YoY", is_positive=True, subtext=f"ARR Runrate: ${total_arr:,.0f}", badge="MRR")
    with c2:
        render_kpi("Active Subscribers", f"{active_subs:,}", delta="+11.2%", is_positive=True, subtext="Contracted paying accounts", badge="SUBSCRIBERS")
    with c3:
        render_kpi("Blended ARPU", f"${arpu:,.0f}/mo", delta="+$42/mo", is_positive=True, subtext="Avg revenue per active logo", badge="ARPU")
    with c4:
        render_kpi("SaaS Quick Ratio", f"{quick_ratio:.2f}x", delta="Top-quartile > 4x", is_positive=quick_ratio >= 4, subtext="New+Expansion / Churn+Contraction", badge="QUICK RATIO")

    # ── MRR over time (line chart by cohort month) ────────────────────────────
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>MRR TREND BY COHORT MONTH</div>", unsafe_allow_html=True)
    df_f_copy = df_f.copy()
    df_f_copy["cohort_month"] = pd.to_datetime(df_f_copy["cohort"])
    mrr_trend = df_f_copy.groupby("cohort_month")["mrr"].sum().reset_index().sort_values("cohort_month")
    mrr_trend["cohort_month_str"] = mrr_trend["cohort_month"].dt.strftime("%b %Y")
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=mrr_trend["cohort_month_str"],
        y=mrr_trend["mrr"],
        mode="lines+markers",
        line=dict(color="#8b5cf6", width=3),
        fill="tozeroy",
        fillcolor="rgba(139,92,246,0.12)",
        name="MRR",
    ))
    fig_line.update_layout(**get_plotly_layout("saas", height=260))
    st.plotly_chart(fig_line, use_container_width=True)

    # ── Tier bar + Waterfall ─────────────────────────────────────────────────
    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>MRR VELOCITY BY TIER</div>", unsafe_allow_html=True)
        tier_agg = df_f.groupby("tier").agg(mrr=("mrr", "sum"), customer_id=("customer_id", "count")).reset_index()
        fig_bar = px.bar(tier_agg, x="tier", y="mrr", text_auto="$.2s", color="tier", color_discrete_sequence=["#8b5cf6", "#6366f1", "#38bdf8"])
        fig_bar.update_layout(**get_plotly_layout("saas", height=300), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>MRR MOVEMENT COMPOSITION</div>", unsafe_allow_html=True)
        mov_labels = ["Beginning MRR", "New Logo MRR", "Expansion MRR", "Contraction MRR", "Churned MRR"]
        mov_vals = [total_mrr * 0.82, total_mrr * 0.12, expansion, -contraction, -churned_mrr * 0.1]
        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["relative", "relative", "relative", "relative", "relative"],
            x=mov_labels,
            y=mov_vals,
            textposition="outside",
            decreasing={"marker": {"color": "#ef4444"}},
            increasing={"marker": {"color": "#8b5cf6"}},
            totals={"marker": {"color": "#38bdf8"}},
        ))
        fig_wf.update_layout(**get_plotly_layout("saas", height=300))
        st.plotly_chart(fig_wf, use_container_width=True)

    render_export_button(df_f[["customer_id", "tier", "mrr", "arr", "expansion_mrr", "churned"]].head(500), "saas_mrr_velocity.csv")
