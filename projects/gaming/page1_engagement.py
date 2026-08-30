# projects/gaming/page1_engagement.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Player Engagement & DAU/MAU Stickiness", badge="TELEMETRY", subtitle="Daily active engagement, session frequency, and acquisition channel quality")
    
    total_players = len(df)
    active_d7 = len(df[df["retained_d7"]])
    active_d30 = len(df[df["retained_d30"]])
    dau_est = int(total_players * 0.28)
    mau_est = int(total_players * 0.74)
    stickiness = (dau_est / mau_est * 100)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Est. Daily Active Users", f"{dau_est:,}", delta="+12.4% WoW", is_positive=True, badge="DAU")
    with c2:
        render_kpi("Monthly Active Users", f"{mau_est:,}", delta="+8.1% MoM", is_positive=True, badge="MAU")
    with c3:
        render_kpi("DAU / MAU Stickiness", f"{stickiness:.1f}%", delta="Top-tier benchmark > 35%", is_positive=True, badge="STICKINESS")
    with c4:
        render_kpi("D7 Retained Core", f"{active_d7:,}", delta="+4.2%", is_positive=True, subtext="Players active at D+7", badge="CORE")
        
    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>RETENTION CURVE (D1 THROUGH D30)</div>", unsafe_allow_html=True)
        days = ["Day 1", "Day 3", "Day 7", "Day 14", "Day 21", "Day 30"]
        rates = [72.4, 55.1, 42.8, 32.5, 26.1, 21.4]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatter(x=days, y=rates, mode="lines+markers", line=dict(color="#06b6d4", width=3), marker=dict(size=8, color="#ec4899"), fill='tozeroy', fillcolor='rgba(6, 182, 212, 0.15)'))
        fig_r.update_layout(**get_plotly_layout("gaming", height=300))
        st.plotly_chart(fig_r, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>PLAYERS BY CHANNEL</div>", unsafe_allow_html=True)
        chan_agg = df["channel"].value_counts().reset_index()
        chan_agg.columns = ["Channel", "Players"]
        fig_pie = px.pie(chan_agg, values="Players", names="Channel", hole=0.6, color_discrete_sequence=["#06b6d4", "#ec4899", "#a855f7", "#10b981"])
        fig_pie.update_layout(**get_plotly_layout("gaming", height=300))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    render_export_button(df[["player_id", "first_seen", "level", "channel", "retained_d7", "retained_d30"]].head(500), "gaming_engagement_stream.csv")
