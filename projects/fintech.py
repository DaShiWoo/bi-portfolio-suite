"""
projects/fintech.py
Fintech & Anti-Fraud Engine Analytics.
Design: Bloomberg Terminal Dark Graphite & Emerald/Gold.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, get_plotly_layout

def render():
    df = pd.read_parquet("data/fintech_transactions.parquet")
    
    total_volume = df["amount"].sum()
    fraud_df = df[df["is_fraud"]]
    fraud_volume = fraud_df["amount"].sum()
    fraud_rate = (len(fraud_df) / len(df)) * 100
    blocked_count = len(df[df["decision"] == "BLOCK"])
    review_count = len(df[df["decision"] == "FLAG_REVIEW"])
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Total Transaction Volume", f"${total_volume:,.0f}", delta="+3.1% 24h", is_positive=True, subtext="15,000 processed txns", badge="VOLUME")
    with c2:
        render_kpi("Fraud Incident Rate", f"{fraud_rate:.2f}%", delta="-0.15%", is_positive=True, subtext=f"Prevented: ${fraud_volume:,.0f}", badge="DEFENSE")
    with c3:
        render_kpi("Rule-Triggered Blocks", f"{blocked_count:,}", delta="+12 incidents", is_positive=False, subtext="Instant automated drop", badge="SECURITY")
    with c4:
        render_kpi("Manual Review Queue", f"{review_count:,}", delta="-8 items", is_positive=True, subtext="Risk Score 65 - 82", badge="OPS")
        
    render_section_header("Live Anomaly Detection & Global Risk Radar", badge="DETECTION")
    col_chart1, col_chart2 = st.columns([7, 5])
    
    with col_chart1:
        # Anomaly Detection Scatter Plot: Amount vs Risk Score
        sample = df.sample(min(800, len(df)))
        fig_scatter = px.scatter(
            sample, x="amount", y="risk_score", color="decision",
            color_discrete_map={"APPROVE": "#10b981", "FLAG_REVIEW": "#f59e0b", "BLOCK": "#ef4444"},
            hover_data=["txn_id", "payment_method", "geo_risk"]
        )
        # Threshold line
        fig_scatter.add_hline(y=82, line_dash="dash", line_color="#ef4444", annotation_text="Auto-Block Threshold")
        fig_scatter.add_hline(y=65, line_dash="dot", line_color="#f59e0b", annotation_text="Review Threshold")
        fig_scatter.update_layout(**get_plotly_layout("fintech", height=340))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_chart2:
        # Risk Radar Chart
        categories = ["High Amount", "Velocity", "New Device", "High-Risk Geo", "Failed CVV", "Web3 Mix"]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[85, 92, 60, 78, 45, 88],
            theta=categories,
            fill='toself',
            fillcolor='rgba(16, 185, 129, 0.25)',
            line=dict(color='#10b981', width=2),
            name='Current Threat Level'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[35, 40, 30, 25, 20, 30],
            theta=categories,
            fill='toself',
            fillcolor='rgba(59, 130, 246, 0.15)',
            line=dict(color='#3b82f6', width=1.5, dash='dot'),
            name='Baseline Norm'
        ))
        layout = get_plotly_layout("fintech", height=340)
        layout["polar"] = dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.08)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.08)', linecolor='rgba(255,255,255,0.1)')
        )
        fig_radar.update_layout(**layout)
        st.plotly_chart(fig_radar, use_container_width=True)
        
    render_section_header("Real-Time Transaction Ledger & Geo Breakdown", badge="TELEMETRY")
    col_t1, col_t2 = st.columns([7, 5])
    with col_t1:
        st.dataframe(
            df[["txn_id", "timestamp", "amount", "payment_method", "geo_risk", "risk_score", "decision"]].head(15),
            use_container_width=True,
            height=280
        )
    with col_t2:
        geo_agg = df.groupby("geo_risk")["amount"].sum().reset_index()
        fig_geo = px.pie(
            geo_agg, values="amount", names="geo_risk", hole=0.55,
            color_discrete_sequence=["#10b981", "#3b82f6", "#ef4444"]
        )
        fig_geo.update_layout(**get_plotly_layout("fintech", height=280))
        st.plotly_chart(fig_geo, use_container_width=True)
