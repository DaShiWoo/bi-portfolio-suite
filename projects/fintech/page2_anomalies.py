# projects/fintech/page2_anomalies.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Anomaly Investigation & Risk Radar", badge="FORENSICS", subtitle="Deep-dive into multi-variate statistical anomalies, outliers, and threshold triggers")
    
    sample = df.sample(min(1000, len(df)))
    anom_count = len(df[df["risk_score"] > 80])
    high_val = len(df[df["amount"] > 10000])
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("High-Score Anomalies", f"{anom_count:,}", delta="+18 detected", is_positive=False, badge="ANOMALIES")
    with c2:
        render_kpi("Whale Transactions (>$10k)", f"{high_val:,}", delta="Monitored transfers", is_positive=True, badge="WHALES")
    with c3:
        render_kpi("Proxy / VPN Usage", f"{(df['proxy_ip'].mean()*100):.1f}%", delta="+0.4% risk", is_positive=False, badge="NETWORK")
    with c4:
        render_kpi("Mean Anomaly Score", f"{df['risk_score'].mean():.1f} / 100", delta="-1.2 pts", is_positive=True, badge="BASELINE")
        
    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>ANOMALY SCATTER (AMOUNT VS RISK SCORE)</div>", unsafe_allow_html=True)
        fig_sc = px.scatter(
            sample, x="amount", y="risk_score", color="decision",
            color_discrete_map={"APPROVE": "#10b981", "FLAG_REVIEW": "#f59e0b", "BLOCK": "#ef4444"},
            hover_data=["txn_id", "payment_method", "jurisdiction"]
        )
        fig_sc.add_hline(y=80, line_dash="dash", line_color="#ef4444", annotation_text="Auto-Block > 80")
        fig_sc.update_layout(**get_plotly_layout("fintech", height=320))
        st.plotly_chart(fig_sc, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>MULTI-VECTOR THREAT RADAR</div>", unsafe_allow_html=True)
        cats = ["Large Value", "Txn Velocity", "New Device", "High-Risk Geo", "Proxy/VPN", "Web3 Hop"]
        fig_rad = go.Figure()
        fig_rad.add_trace(go.Scatterpolar(r=[85, 92, 60, 78, 65, 88], theta=cats, fill='toself', fillcolor='rgba(16, 185, 129, 0.25)', line=dict(color='#10b981', width=2), name='Active Threat'))
        fig_rad.add_trace(go.Scatterpolar(r=[35, 40, 30, 25, 20, 30], theta=cats, fill='toself', fillcolor='rgba(59, 130, 246, 0.15)', line=dict(color='#3b82f6', width=1.5, dash='dot'), name='Baseline Norm'))
        layout = get_plotly_layout("fintech", height=320)
        layout["polar"] = dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.08)'))
        fig_rad.update_layout(**layout)
        st.plotly_chart(fig_rad, use_container_width=True)
        
    render_export_button(df[df["risk_score"] > 75].head(500), "forensic_anomalies_export.csv")
