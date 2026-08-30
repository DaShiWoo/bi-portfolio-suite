# projects/marketplace/page3_marketing.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Marketing Performance & Attribution", badge="ATTRIBUTION", subtitle="Paid campaigns efficiency, ACoS (ДРР), ROAS, and channel contribution")
    
    total_gmv = df["amount"].sum()
    est_ad_spend = total_gmv * 0.082
    blended_roas = (total_gmv / est_ad_spend) if est_ad_spend > 0 else 0
    acos = (est_ad_spend / total_gmv * 100) if total_gmv > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Total Ad Spend", f"${est_ad_spend:,.0f}", delta="+6.4%", is_positive=False, subtext="Blended paid media spend", badge="SPEND")
    with c2:
        render_kpi("Blended ROAS", f"{blended_roas:.2f}x", delta="+0.35x", is_positive=True, subtext="Attributed GMV / Ad Spend", badge="ROAS")
    with c3:
        render_kpi("ACoS (ДРР)", f"{acos:.1f}%", delta="-0.8%", is_positive=True, subtext="Advertising Cost of Sales", badge="ACOS")
    with c4:
        render_kpi("Avg Cost-Per-Click", "$0.48", delta="-$0.04", is_positive=True, subtext="Across Search & Social", badge="CPC")
        
    c1, c2 = st.columns([7, 5])
    with c1:
        chan_agg = df.groupby("channel").agg({"amount": "sum", "order_id": "count"}).reset_index()
        chan_agg["spend"] = chan_agg["amount"] * np.random.uniform(0.06, 0.11, len(chan_agg))
        chan_agg["roas"] = (chan_agg["amount"] / chan_agg["spend"]).round(2)
        fig_scatter = px.scatter(
            chan_agg, x="spend", y="amount", size="order_id", color="channel",
            text="channel", hover_data=["roas"],
            color_discrete_sequence=["#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6"]
        )
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(**get_plotly_layout("marketplace", height=320))
        st.plotly_chart(fig_scatter, use_container_width=True)
    with c2:
        fig_bar = px.bar(chan_agg, x="channel", y="roas", color="roas", color_continuous_scale=["#78350f", "#f59e0b"])
        fig_bar.update_layout(**get_plotly_layout("marketplace", height=320), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    render_export_button(chan_agg, "marketing_channel_performance.csv")
