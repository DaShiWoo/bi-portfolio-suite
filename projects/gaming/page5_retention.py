# projects/gaming/page5_retention.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Retention Benchmark Simulator", badge="WHAT-IF SIMULATOR", subtitle="Interactive game tuning: simulate onboarding difficulty vs D1, D7, and D30 cohort curves")
    
    st.markdown("""
    <div class="what-if-container">
        <span style="font-weight: 700; color: #06b6d4; font-size: 0.95rem;">🔮 INTERACTIVE WHAT-IF SCENARIO: ONBOARDING FRICTION OPTIMIZATION</span>
        <div style="font-size: 0.8rem; color: #a5f3fc; margin-top: 4px;">Model how reducing early-game friction shifts D1, D7, and D30 cohort retention curves:</div>
    </div>
    """, unsafe_allow_html=True)
    
    d1_boost = st.slider("Simulated D1 Retention Boost (+%)", min_value=0.0, max_value=15.0, value=6.0, step=0.5)
    
    base_d1, base_d7, base_d30 = 70.0, 42.0, 21.0
    sim_d1 = min(95.0, base_d1 + d1_boost)
    sim_d7 = min(80.0, base_d7 + (d1_boost * 0.75))
    sim_d30 = min(60.0, base_d30 + (d1_boost * 0.55))
    
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi("Simulated D1 Retention", f"{sim_d1:.1f}%", delta=f"+{d1_boost:.1f}% vs baseline", is_positive=True, badge="DAY 1")
    with c2:
        render_kpi("Simulated D7 Retention", f"{sim_d7:.1f}%", delta=f"+{sim_d7-base_d7:.1f}% cascade", is_positive=True, badge="DAY 7")
    with c3:
        render_kpi("Simulated D30 Retention", f"{sim_d30:.1f}%", delta=f"+{sim_d30-base_d30:.1f}% long-term", is_positive=True, badge="DAY 30")
        
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>SIMULATED RETENTION CURVE TRAJECTORY</div>", unsafe_allow_html=True)
    days = ["D1", "D3", "D7", "D14", "D21", "D30"]
    base_curve = [base_d1, 54.0, base_d7, 31.0, 25.0, base_d30]
    sim_curve = [sim_d1, 54.0 + d1_boost*0.85, sim_d7, 31.0 + d1_boost*0.65, 25.0 + d1_boost*0.6, sim_d30]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=base_curve, name="Status Quo Curve", line=dict(color="rgba(255,255,255,0.4)", width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=days, y=sim_curve, name="Optimized Retention Curve", line=dict(color="#06b6d4", width=3), marker=dict(size=8, color="#ec4899"), fill='tonexty', fillcolor='rgba(6, 182, 212, 0.15)'))
    fig.update_layout(**get_plotly_layout("gaming", height=300))
    st.plotly_chart(fig, use_container_width=True)
    
    render_export_button(pd.DataFrame({"Day": days, "Baseline": base_curve, "Simulated": sim_curve}), "retention_simulation_export.csv")
