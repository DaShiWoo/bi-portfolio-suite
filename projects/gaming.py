"""
projects/gaming.py
Video Game LiveOps & Economy BI Analytics Dashboard.
Design: Cyber Neon Arcade (Deep Space, Cyan & Magenta).
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, get_plotly_layout

def render():
    df = pd.read_parquet("data/gaming_telemetry.parquet")
    
    total_players = len(df)
    paying_players = df[df["iap_spend_usd"] > 0]
    total_revenue = df["iap_spend_usd"].sum()
    arppu = total_revenue / len(paying_players) if len(paying_players) > 0 else 0
    d7_retention = df["retained_d7"].mean() * 100
    d30_retention = df["retained_d30"].mean() * 100
    total_gold_circulating = df["gold_balance"].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Live Players (Installs)", f"{total_players:,}", delta="+15.2% WoW", is_positive=True, subtext="Organic & UA installs", badge="DAU/MAU")
    with c2:
        render_kpi("IAP & Battlepass Gross", f"${total_revenue:,.0f}", delta="+22.8% WoW", is_positive=True, subtext=f"ARPPU: ${arppu:.2f}", badge="MONETIZATION")
    with c3:
        render_kpi("D7 Cohort Retention", f"{d7_retention:.1f}%", delta="+2.4%", is_positive=True, subtext=f"D30 Benchmark: {d30_retention:.1f}%", badge="ENGAGEMENT")
    with c4:
        render_kpi("Virtual Currency Pool", f"{total_gold_circulating / 1e6:.2f}M Gold", delta="-1.5%", is_positive=True, subtext="Controlled Sink/Source ratio", badge="ECONOMY")
        
    render_section_header("Level Progression & Churn Funnel", badge="PROGRESSION", subtitle="Pinpointing exact player friction points across level milestones")
    c_mid1, c_mid2 = st.columns([7, 5])
    
    with c_mid1:
        # Player distribution across level brackets
        bins = [0, 5, 10, 20, 35, 50]
        labels = ["Lvl 1-5 (Onboarding)", "Lvl 6-10 (Early)", "Lvl 11-20 (Midgame)", "Lvl 21-35 (Core)", "Lvl 36-50 (Endgame)"]
        df["bracket"] = pd.cut(df["level_reached"], bins=bins, labels=labels)
        bracket_agg = df["bracket"].value_counts().reindex(labels).reset_index()
        bracket_agg.columns = ["Bracket", "Players"]
        
        fig_funnel = go.Figure(go.Funnel(
            y=bracket_agg["Bracket"],
            x=bracket_agg["Players"],
            textinfo="value+percent initial",
            marker=dict(color=["#06b6d4", "#38bdf8", "#818cf8", "#c084fc", "#ec4899"])
        ))
        fig_funnel.update_layout(**get_plotly_layout("gaming", height=320))
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    with c_mid2:
        # Sink vs Source Sankey / Flow or Donut
        econ_labels = ["Quests & Drops", "Achievements", "IAP Packs", "Cosmetic Skins", "Weapon Crafting", "Battlepass Entry"]
        econ_values = [42, 18, 40, 35, 45, 20]
        fig_donut = px.pie(
            values=econ_values, names=econ_labels, hole=0.6,
            color_discrete_sequence=["#06b6d4", "#ec4899", "#a855f7", "#3b82f6", "#eab308", "#10b981"]
        )
        fig_donut.update_layout(**get_plotly_layout("gaming", height=320))
        st.plotly_chart(fig_donut, use_container_width=True)
        
    render_section_header("Acquisition Channel Performance & Monetization", badge="UA MARKETING")
    c_bot1, c_bot2 = st.columns(2)
    
    with c_bot1:
        chan_agg = df.groupby("source_channel").agg({"iap_spend_usd": "sum", "player_id": "count"}).reset_index()
        fig_chan = px.bar(
            chan_agg, x="source_channel", y="iap_spend_usd",
            color="source_channel", color_discrete_sequence=["#06b6d4", "#ec4899", "#a855f7", "#10b981"]
        )
        fig_chan.update_layout(**get_plotly_layout("gaming", height=290), showlegend=False)
        st.plotly_chart(fig_chan, use_container_width=True)
        
    with c_bot2:
        # Retention curve line chart
        days = [1, 3, 7, 14, 21, 30]
        ret_rates = [72, 54, 42, 31, 25, 21]
        fig_ret = go.Figure()
        fig_ret.add_trace(go.Scatter(
            x=[f"Day {d}" for d in days], y=ret_rates, mode="lines+markers",
            line=dict(color="#ec4899", width=3),
            marker=dict(size=8, color="#06b6d4"),
            fill='tozeroy', fillcolor='rgba(236, 72, 153, 0.15)'
        ))
        fig_ret.update_layout(**get_plotly_layout("gaming", height=290))
        st.plotly_chart(fig_ret, use_container_width=True)
