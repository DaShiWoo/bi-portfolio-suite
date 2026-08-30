# projects/fintech/page4_geo.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Cross-Border Geolocation Risk Matrix", badge="JURISDICTIONS", subtitle="Tracking international settlement flows, high-risk territorial hubs, and sanction screening")
    
    geo_agg = df.groupby("jurisdiction").agg(
        volume=("amount", "sum"),
        txns=("txn_id", "count"),
        fraud_txns=("is_fraud", "sum"),
        mean_score=("risk_score", "mean")
    ).reset_index()
    geo_agg["fraud_rate"] = (geo_agg["fraud_txns"] / geo_agg["txns"] * 100).round(2)
    
    offshore = geo_agg[geo_agg["jurisdiction"] == "Offshore / High-Risk"]
    offshore_rate = offshore["fraud_rate"].values[0] if len(offshore) > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Domestic Traffic Share", "45.0%", delta="Core safe volume", is_positive=True, badge="DOMESTIC")
    with c2:
        render_kpi("Offshore Fraud Rate", f"{offshore_rate:.1f}%", delta="Critical risk factor", is_positive=False, badge="OFFSHORE")
    with c3:
        render_kpi("Cross-Border Volume", f"${df[df['jurisdiction']!='North America']['amount'].sum():,.0f}", delta="+8.2%", is_positive=True, badge="GLOBAL")
    with c4:
        render_kpi("High-Risk Block Ratio", "84.2%", delta="Automated perimeter", is_positive=True, badge="ENFORCE")
        
    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>VOLUME CONTRIBUTION BY GEOGRAPHY</div>", unsafe_allow_html=True)
        fig_pie = px.pie(geo_agg, values="volume", names="jurisdiction", hole=0.55, color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ec4899", "#ef4444"])
        fig_pie.update_layout(**get_plotly_layout("fintech", height=300))
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>FRAUD RATE BY JURISDICTION (%)</div>", unsafe_allow_html=True)
        fig_bar = px.bar(geo_agg, x="jurisdiction", y="fraud_rate", color="fraud_rate", color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"])
        fig_bar.update_layout(**get_plotly_layout("fintech", height=300), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    render_export_button(geo_agg, "geolocation_risk_matrix.csv")
