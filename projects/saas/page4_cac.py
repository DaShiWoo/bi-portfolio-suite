# projects/saas/page4_cac.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Customer Acquisition Cost & Payback Velocity", badge="UNIT ECONOMICS", subtitle="CAC by channel, months to recover acquisition spend, and LTV:CAC efficiency ratios")
    
    avg_cac = df["cac"].mean()
    active_df = df[~df["churned"]]
    arpu = active_df["mrr"].mean()
    payback_months = (avg_cac / arpu) if arpu > 0 else 0
    ltv = arpu * 28.0 # ~28 month average customer lifespan
    ltv_cac_ratio = (ltv / avg_cac) if avg_cac > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Blended CAC", f"${avg_cac:,.0f}", delta="-$180 vs budget", is_positive=True, subtext="Cost to acquire paying logo", badge="CAC")
    with c2:
        render_kpi("CAC Payback Period", f"{payback_months:.1f} months", delta="-1.2 mo", is_positive=True, subtext="Target: < 12 months", badge="PAYBACK")
    with c3:
        render_kpi("LTV : CAC Ratio", f"{ltv_cac_ratio:.2f}x", delta="Top quartile > 3x", is_positive=True, subtext=f"Estimated LTV: ${ltv:,.0f}", badge="EFFICIENCY")
    with c4:
        render_kpi("Inbound Channel Share", "42%", delta="+5% YoY", is_positive=True, subtext="Lowest CAC acquisition vector", badge="INBOUND")
        
    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>CAC AND ARPU BY ACQUISITION CHANNEL</div>", unsafe_allow_html=True)
        chan_cac = df.groupby("channel").agg({"cac": "mean", "mrr": "mean", "customer_id": "count"}).reset_index()
        fig_bar = px.bar(
            chan_cac, x="channel", y=["cac", "mrr"], barmode="group",
            color_discrete_sequence=["#8b5cf6", "#38bdf8"]
        )
        fig_bar.update_layout(**get_plotly_layout("saas", height=300))
        st.plotly_chart(fig_bar, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>CAC PAYBACK TIMELINE (MONTHS TO BREAKEVEN)</div>", unsafe_allow_html=True)
        chan_cac["payback"] = (chan_cac["cac"] / chan_cac["mrr"]).round(1)
        fig_p = px.bar(chan_cac, x="channel", y="payback", text_auto='true', color="payback", color_continuous_scale=["#10b981", "#8b5cf6", "#ef4444"])
        fig_p.update_layout(**get_plotly_layout("saas", height=300), coloraxis_showscale=False)
        st.plotly_chart(fig_p, use_container_width=True)
        
    render_export_button(chan_cac, "cac_channel_breakdown.csv")
