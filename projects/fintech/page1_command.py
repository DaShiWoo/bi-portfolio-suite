# projects/fintech/page1_command.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Live Threat Command Center", badge="REAL-TIME MONITORING", subtitle="Global transaction stream telemetry, real-time threat score, and instant automated mitigation")
    
    vol = df["amount"].sum()
    fraud_df = df[df["is_fraud"]]
    prevented = fraud_df["amount"].sum()
    fraud_pct = (len(fraud_df) / len(df)) * 100
    blocked = len(df[df["decision"] == "BLOCK"])
    review = len(df[df["decision"] == "FLAG_REVIEW"])
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("24h Transaction Volume", f"${vol:,.0f}", delta="+3.1% volume", is_positive=True, subtext="15,000 processed transactions", badge="THROUGHPUT")
    with c2:
        render_kpi("Fraud Incident Rate", f"{fraud_pct:.2f}%", delta="-0.18% 24h", is_positive=True, subtext=f"Prevented Loss: ${prevented:,.0f}", badge="DEFENSE")
    with c3:
        render_kpi("Automated Blocks", f"{blocked:,}", delta="+14 blocked", is_positive=False, subtext="Risk threshold > 80.0", badge="SECURITY")
    with c4:
        render_kpi("Review Queue Pending", f"{review:,}", delta="-6 resolved", is_positive=True, subtext="Manual compliance checks", badge="QUEUE")
        
    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>LIVE TRANSACTION FLOW BY METHOD</div>", unsafe_allow_html=True)
        m_agg = df.groupby("payment_method").agg({"amount": "sum", "is_fraud": "sum"}).reset_index()
        fig_m = px.bar(m_agg, x="payment_method", y="amount", color="payment_method", color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ec4899"])
        fig_m.update_layout(**get_plotly_layout("fintech", height=300), showlegend=False)
        st.plotly_chart(fig_m, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>AUTOMATED RISK DECISION SPLIT</div>", unsafe_allow_html=True)
        dec_agg = df["decision"].value_counts().reset_index()
        dec_agg.columns = ["Decision", "Count"]
        fig_pie = px.pie(dec_agg, values="Count", names="Decision", hole=0.6, color="Decision", color_discrete_map={"APPROVE": "#10b981", "FLAG_REVIEW": "#f59e0b", "BLOCK": "#ef4444"})
        fig_pie.update_layout(**get_plotly_layout("fintech", height=300))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    render_export_button(df[["txn_id", "timestamp", "amount", "payment_method", "risk_score", "decision"]].head(500), "fintech_command_stream.csv")
