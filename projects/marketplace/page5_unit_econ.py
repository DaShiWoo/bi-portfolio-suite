# projects/marketplace/page5_unit_econ.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Unit Economics & What-If Fee Simulator", badge="PROFITABILITY", subtitle="Waterfall margin breakdown per order, LTV dynamics, and interactive fee modeling")
    
    # What-If Simulator
    st.markdown("""
    <div class="what-if-container">
        <span style="font-weight: 700; color: #f59e0b; font-size: 0.95rem;">🔮 INTERACTIVE WHAT-IF SCENARIO: COMMISSION FEE ADJUSTMENT</span>
        <div style="font-size: 0.8rem; color: #a1a1aa; margin-top: 4px;">Simulate the net revenue impact of altering marketplace take-rate commission:</div>
    </div>
    """, unsafe_allow_html=True)
    
    sim_take_rate = st.slider("Simulated Marketplace Take Rate (%)", min_value=8.0, max_value=25.0, value=15.2, step=0.2)
    
    base_gmv = df["amount"].sum()
    sim_rev = base_gmv * (sim_take_rate / 100.0)
    actual_rev = df["marketplace_fee"].sum()
    rev_delta = sim_rev - actual_rev
    
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi("Simulated Annual Net Revenue", f"${sim_rev:,.0f}", delta=f"{rev_delta:+,.0f} vs actual", is_positive=rev_delta>=0, badge="SIMULATED")
    with c2:
        render_kpi("Customer Acquisition Cost", "$24.50", delta="Healthy 3.8x LTV:CAC", is_positive=True, badge="CAC")
    with c3:
        render_kpi("Estimated 12M LTV", "$93.20", delta="+12.4% YoY", is_positive=True, badge="LTV")
        
    render_section_header("Unit Economic Waterfall (Per $100 GMV)", badge="WATERFALL")
    fig_wf = go.Figure(go.Waterfall(
        name="Unit Margin", orientation="v",
        measure=["relative", "relative", "relative", "relative", "total"],
        x=["Buyer Payment (GMV)", "Seller Payout (-85%)", "Payment Gateway (-2.5%)", "Platform Ops (-3.5%)", "Net Contribution"],
        textposition="outside",
        text=["+$100.0", "-$85.0", "-$2.5", "-$3.5", "+$9.0"],
        y=[100.0, -85.0, -2.5, -3.5, 0],
        connector={"line": {"color": "rgba(255,255,255,0.2)"}},
        decreasing={"marker": {"color": "#ef4444"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#f59e0b"}}
    ))
    fig_wf.update_layout(**get_plotly_layout("marketplace", height=320))
    st.plotly_chart(fig_wf, use_container_width=True)
    
    render_export_button(pd.DataFrame([{"Base GMV": base_gmv, "Simulated Take Rate": sim_take_rate, "Simulated Revenue": sim_rev, "Actual Revenue": actual_rev}]), "scenario_modeling_export.csv")
