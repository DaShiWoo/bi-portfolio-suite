# projects/fintech/page3_rails.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Payment Rails & Gateway Economics", badge="RAILS", subtitle="Comparative throughput, authorization rates, and chargeback exposure across rails")
    
    m_agg = df.groupby("payment_method").agg(
        total_vol=("amount", "sum"),
        txn_count=("txn_id", "count"),
        fraud_vol=("amount", lambda x: x[df.loc[x.index, "is_fraud"]].sum()),
        mean_risk=("risk_score", "mean")
    ).reset_index()
    m_agg["fraud_rate"] = (m_agg["fraud_vol"] / m_agg["total_vol"] * 100).round(2)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Card Authorization Rate", "97.4%", delta="+0.6%", is_positive=True, badge="CARDS")
    with c2:
        render_kpi("Wire Settlement Volume", f"${m_agg[m_agg['payment_method']=='Wire Transfer']['total_vol'].values[0]:,.0f}", badge="WIRE")
    with c3:
        render_kpi("Web3/Crypto Fraud Rate", f"{m_agg[m_agg['payment_method']=='Web3/Crypto']['fraud_rate'].values[0]:.2f}%", delta="Highest risk vector", is_positive=False, badge="WEB3")
    with c4:
        render_kpi("Instant ACH Reliability", "99.1%", delta="+0.1%", is_positive=True, badge="ACH")
        
    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>VOLUME AND FRAUD BY RAIL</div>", unsafe_allow_html=True)
        fig_r = px.bar(m_agg, x="payment_method", y=["total_vol", "fraud_vol"], barmode="group", color_discrete_sequence=["#10b981", "#ef4444"])
        fig_r.update_layout(**get_plotly_layout("fintech", height=300))
        st.plotly_chart(fig_r, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>MEAN RISK SCORE BY PAYMENT RAIL</div>", unsafe_allow_html=True)
        fig_mr = px.bar(m_agg, x="payment_method", y="mean_risk", color="mean_risk", color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"])
        fig_mr.update_layout(**get_plotly_layout("fintech", height=300), coloraxis_showscale=False)
        st.plotly_chart(fig_mr, use_container_width=True)
        
    render_export_button(m_agg, "payment_rails_economics.csv")
