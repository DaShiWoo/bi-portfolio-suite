"""
projects/saas.py
B2B SaaS & Subscriptions Intelligence Dashboard.
Design: Linear App Dark & Stripe Royal Indigo.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, get_plotly_layout

def render():
    df = pd.read_parquet("data/saas_subscriptions.parquet")
    
    # KPIs
    total_mrr = df["mrr"].sum()
    total_arr = df["arr"].sum()
    active_customers = len(df[~df["churned"]])
    churn_rate = (df["churned"].mean() * 100)
    avg_cac = df["cac"].mean()
    arpu = total_mrr / active_customers if active_customers > 0 else 0
    cac_payback_months = (avg_cac / arpu) if arpu > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Monthly Recurring Revenue", f"${total_mrr:,.0f}", delta="+18.4% MoM", is_positive=True, subtext=f"ARR Runrate: ${total_arr:,.0f}", badge="MRR")
    with c2:
        render_kpi("Active Subscribers", f"{active_customers:,}", delta="+11.2%", is_positive=True, subtext=f"Logo Churn: {churn_rate:.1f}%", badge="SCALE")
    with c3:
        render_kpi("Average Revenue Per User", f"${arpu:.0f}/mo", delta="+6.7%", is_positive=True, subtext="Blended ARPU across tiers", badge="ARPU")
    with c4:
        render_kpi("CAC Payback Period", f"{cac_payback_months:.1f} mo", delta="-0.8 mo", is_positive=True, subtext=f"Blended CAC: ${avg_cac:,.0f}", badge="EFFICIENCY")
        
    render_section_header("Net Revenue Retention (NRR) Cohort Heatmap", badge="RETENTION", subtitle="Cohort retention tracking expansion & churn across subscription lifecycles")
    
    # Build synthetic cohort matrix
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    cohort_data = []
    for i, m in enumerate(months):
        row = []
        base = 100
        for j in range(len(months)):
            if j < i:
                row.append(None)
            elif j == i:
                row.append(100)
            else:
                # Typical B2B SaaS NRR with expansion
                diff = j - i
                expansion = 100 + (diff * 2.8) - (diff * 0.9) + np.random.normal(0, 1.2)
                row.append(round(expansion, 1))
        cohort_data.append(row)
        
    fig_heat = px.imshow(
        cohort_data,
        x=[f"M+{i}" for i in range(len(months))],
        y=[f"{m} 24" for m in months],
        color_continuous_scale=[[0, "#0b0d17"], [0.5, "#3b2d6b"], [1, "#8b5cf6"]],
        text_auto=True,
        aspect="auto"
    )
    fig_heat.update_layout(**get_plotly_layout("saas", height=320))
    fig_heat.update_coloraxes(showscale=False)
    st.plotly_chart(fig_heat, use_container_width=True)
    
    render_section_header("Tier Breakdown & Expansion Revenue vs Churn", badge="UNIT ECONOMICS")
    c_bot1, c_bot2 = st.columns(2)
    
    with c_bot1:
        tier_agg = df.groupby("tier").agg({"mrr": "sum", "customer_id": "count"}).reset_index()
        fig_bar = px.bar(
            tier_agg, x="tier", y="mrr", text_auto='$.2s',
            color="tier", color_discrete_sequence=["#8b5cf6", "#6366f1", "#38bdf8"]
        )
        fig_bar.update_layout(**get_plotly_layout("saas", height=290), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c_bot2:
        # Scatter: CAC vs MRR with Tier
        fig_scatter = px.scatter(
            df.sample(min(400, len(df))), x="cac", y="mrr", color="tier",
            size="expansion_revenue", hover_data=["customer_id"],
            color_discrete_sequence=["#8b5cf6", "#38bdf8", "#ec4899"]
        )
        fig_scatter.update_layout(**get_plotly_layout("saas", height=290))
        st.plotly_chart(fig_scatter, use_container_width=True)
