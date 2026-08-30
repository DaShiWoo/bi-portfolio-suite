# projects/saas/page5_forecast.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Scenario Forecasting & Churn Reduction Simulator", badge="PREDICTIVE", subtitle="Interactive simulation modeling compound ARR trajectory under varying churn & expansion parameters")
    
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
        
    current_mrr = df["mrr"].sum()
    months_ahead = 24
    
    # Simulate base trajectory vs optimized trajectory
    base_proj = []
    opt_proj = []
    curr_base = current_mrr
    curr_opt = current_mrr
    
    for _ in range(months_ahead):
        curr_base = curr_base * (1 + 0.025 - 0.015) # +1% net growth
        curr_opt = curr_opt * (1 + 0.025 + (expansion_boost_pct/100) - (0.015 - (churn_reduction_pct/100)))
        base_proj.append(curr_base)
        opt_proj.append(curr_opt)
        
    delta_arr = (opt_proj[-1] - base_proj[-1]) * 12
    
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi("Current Baseline ARR", f"${current_mrr*12:,.0f}", badge="CURRENT")
    with c2:
        render_kpi("Optimized 24M ARR Target", f"${opt_proj[-1]*12:,.0f}", delta=f"+${delta_arr:,.0f} ARR Lift", is_positive=True, badge="FORECAST")
    with c3:
        render_kpi("Retention Compounding Delta", f"+{(opt_proj[-1]/base_proj[-1]-1)*100:.1f}%", is_positive=True, subtext="Compounded over 24 months", badge="LEVERAGE")
        
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>24-MONTH ARR PROJECTION TRAJECTORY</div>", unsafe_allow_html=True)
    months_labels = [f"M+{i+1}" for i in range(months_ahead)]
    fig_proj = go.Figure()
    fig_proj.add_trace(go.Scatter(
        x=months_labels, y=[b*12 for b in base_proj], name="Status Quo Baseline",
        line=dict(color="rgba(148, 163, 184, 0.6)", width=2, dash="dash")
    ))
    fig_proj.add_trace(go.Scatter(
        x=months_labels, y=[o*12 for o in opt_proj], name="Optimized Trajectory",
        line=dict(color="#8b5cf6", width=3),
        fill='tonexty', fillcolor='rgba(139, 92, 246, 0.12)'
    ))
    fig_proj.update_layout(**get_plotly_layout("saas", height=320))
    st.plotly_chart(fig_proj, use_container_width=True)
    
    render_export_button(pd.DataFrame({"Month": months_labels, "Baseline_ARR": [b*12 for b in base_proj], "Optimized_ARR": [o*12 for o in opt_proj]}), "arr_scenario_projection.csv")
