"""
projects/marketplace.py
Marketplace & E-Commerce Analytics Dashboard.
Design: Vercel Monochrome & Electric Amber.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, get_plotly_layout

def render():
    df = pd.read_parquet("data/marketplace_orders.parquet")
    
    # Global Filters in Expander
    with st.expander("Filter Marketplace Transactions", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            cats = st.multiselect("Category", options=df["category"].unique(), default=df["category"].unique())
        with c2:
            regions = st.multiselect("Region", options=df["region"].unique(), default=df["region"].unique())
        with c3:
            statuses = st.multiselect("Status", options=df["status"].unique(), default=df["status"].unique())
            
    filtered = df[(df["category"].isin(cats)) & (df["region"].isin(regions)) & (df["status"].isin(statuses))]
    
    # Top KPIs
    gmv = filtered["amount"].sum()
    revenue = filtered["marketplace_fee"].sum()
    take_rate = (revenue / gmv * 100) if gmv > 0 else 0
    orders_count = len(filtered)
    aov = (gmv / orders_count) if orders_count > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Gross Merchandise Value", f"${gmv:,.0f}", delta="+14.2% MoM", is_positive=True, subtext="12-month rolling GMV", badge="GMV")
    with c2:
        render_kpi("Net Marketplace Revenue", f"${revenue:,.0f}", delta="+16.8% MoM", is_positive=True, subtext=f"Take Rate: {take_rate:.1f}%", badge="TAKE")
    with c3:
        render_kpi("Total Orders Count", f"{orders_count:,}", delta="+8.5%", is_positive=True, subtext=f"AOV: ${aov:.1f}", badge="VOLUME")
    with c4:
        delivered_pct = (filtered['status'] == 'Delivered').mean() * 100
        render_kpi("Fulfillment Rate", f"{delivered_pct:.1f}%", delta="+1.2%", is_positive=True, subtext="Delivered / Dispatched", badge="FULFILL")
        
    render_section_header("Revenue Trajectory & Category Share", badge="TRENDS")
    col_chart1, col_chart2 = st.columns([7, 5])
    
    with col_chart1:
        # Time series aggregated by week
        ts = filtered.copy()
        ts["week"] = ts["timestamp"].dt.to_period("W").dt.to_timestamp()
        weekly = ts.groupby("week").agg({"amount": "sum", "marketplace_fee": "sum"}).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weekly["week"], y=weekly["amount"], name="GMV",
            line=dict(color="#f59e0b", width=3),
            fill='tozeroy', fillcolor='rgba(245, 158, 11, 0.08)'
        ))
        fig.add_trace(go.Scatter(
            x=weekly["week"], y=weekly["marketplace_fee"], name="Net Revenue",
            line=dict(color="#10b981", width=2.5, dash="dot")
        ))
        fig.update_layout(**get_plotly_layout("marketplace", height=340))
        st.plotly_chart(fig, use_container_width=True)
        
    with col_chart2:
        cat_agg = filtered.groupby("category")["amount"].sum().reset_index()
        fig_donut = px.pie(
            cat_agg, values="amount", names="category", hole=0.62,
            color_discrete_sequence=["#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6"]
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(**get_plotly_layout("marketplace", height=340))
        st.plotly_chart(fig_donut, use_container_width=True)
        
    render_section_header("Conversion Funnel & Regional Distribution", badge="LOGISTICS")
    c_bot1, c_bot2 = st.columns(2)
    
    with c_bot1:
        status_counts = filtered["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_funnel = go.Figure(go.Funnel(
            y=status_counts["Status"],
            x=status_counts["Count"],
            textinfo="value+percent initial",
            marker=dict(color=["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#a855f7"])
        ))
        fig_funnel.update_layout(**get_plotly_layout("marketplace", height=300))
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    with c_bot2:
        reg_agg = filtered.groupby("region")["amount"].sum().sort_values(ascending=True).reset_index()
        fig_bar = px.bar(
            reg_agg, x="amount", y="region", orientation="h",
            color="amount", color_continuous_scale=["#18181b", "#f59e0b"]
        )
        fig_bar.update_layout(**get_plotly_layout("marketplace", height=300), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
