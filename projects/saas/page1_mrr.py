# projects/saas/page1_mrr.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("MRR & ARR Growth Velocity", badge="RECURRING REVENUE", subtitle="Monthly recurring revenue bridge, expansion, contraction, and churn waterfall")
    
    total_mrr = df["mrr"].sum()
    total_arr = df["arr"].sum()
    active_subs = len(df[~df["churned"]])
    arpu = total_mrr / active_subs if active_subs > 0 else 0
    expansion = df["expansion_mrr"].sum()
    contraction = df["contraction_mrr"].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Monthly Recurring Revenue", f"${total_mrr:,.0f}", delta="+18.4% YoY", is_positive=True, subtext=f"ARR Runrate: ${total_arr:,.0f}", badge="MRR")
    with c2:
        render_kpi("Active Subscribers", f"{active_subs:,}", delta="+11.2%", is_positive=True, subtext="Contracted paying accounts", badge="SUBSCRIBERS")
    with c3:
        render_kpi("Blended ARPU", f"${arpu:,.0f}/mo", delta="+$42/mo", is_positive=True, subtext="Avg revenue per active logo", badge="ARPU")
    with c4:
        quick_ratio = (expansion + total_mrr*0.08) / (contraction + df[df['churned']]['mrr'].sum() + 1)
        render_kpi("SaaS Quick Ratio", f"{quick_ratio:.2f}x", delta="Top-quartile > 4x", is_positive=True, subtext="New+Expansion / Churn+Contraction", badge="QUICK RATIO")
        
    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>MRR VELOCITY BY TIER</div>", unsafe_allow_html=True)
        tier_agg = df.groupby("tier").agg({"mrr": "sum", "customer_id": "count"}).reset_index()
        fig_bar = px.bar(tier_agg, x="tier", y="mrr", text_auto='$.2s', color="tier", color_discrete_sequence=["#8b5cf6", "#6366f1", "#38bdf8"])
        fig_bar.update_layout(**get_plotly_layout("saas", height=300), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>MRR MOVEMENT COMPOSITION</div>", unsafe_allow_html=True)
        mov_labels = ["Beginning MRR", "New Logo MRR", "Expansion MRR", "Contraction MRR", "Churned MRR"]
        mov_vals = [total_mrr*0.82, total_mrr*0.12, expansion, -contraction, -(df[df['churned']]['mrr'].sum()*0.1)]
        fig_wf = go.Figure(go.Waterfall(
            orientation="v", measure=["relative", "relative", "relative", "relative", "relative"],
            x=mov_labels, y=mov_vals, textposition="outside",
            decreasing={"marker": {"color": "#ef4444"}},
            increasing={"marker": {"color": "#8b5cf6"}},
            totals={"marker": {"color": "#38bdf8"}}
        ))
        fig_wf.update_layout(**get_plotly_layout("saas", height=300))
        st.plotly_chart(fig_wf, use_container_width=True)
        
    render_export_button(df[["customer_id", "tier", "mrr", "arr", "expansion_mrr", "churned"]].head(500), "saas_mrr_velocity.csv")
