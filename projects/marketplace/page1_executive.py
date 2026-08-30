# projects/marketplace/page1_executive.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Executive Macro Performance", badge="MACRO OVERVIEW", subtitle="Top-line GMV, net revenue, take rate economics, and order fulfillment")
    
    gmv = df["amount"].sum()
    rev = df["marketplace_fee"].sum()
    take_rate = (rev / gmv * 100) if gmv > 0 else 0
    orders = len(df)
    aov = gmv / orders if orders > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Gross Merchandise Value", f"${gmv:,.0f}", delta="+14.2% YoY", is_positive=True, subtext="12-month transaction runrate", badge="GMV")
    with c2:
        render_kpi("Net Marketplace Revenue", f"${rev:,.0f}", delta="+16.8% YoY", is_positive=True, subtext=f"Blended Take Rate: {take_rate:.1f}%", badge="REVENUE")
    with c3:
        render_kpi("Total Order Volume", f"{orders:,}", delta="+8.5%", is_positive=True, subtext=f"Average Order Value: ${aov:.1f}", badge="ORDERS")
    with c4:
        margin = (df["profit"].sum() / rev * 100) if rev > 0 else 0
        render_kpi("Operating Net Margin", f"{margin:.1f}%", delta="+2.1%", is_positive=True, subtext=f"Net Profit: ${df['profit'].sum():,.0f}", badge="MARGIN")
        
    c_left, c_right = st.columns([7, 5])
    with c_left:
        ts = df.copy()
        ts["week"] = ts["timestamp"].dt.to_period("W").dt.to_timestamp()
        weekly = ts.groupby("week").agg({"amount": "sum", "marketplace_fee": "sum"}).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=weekly["week"], y=weekly["amount"], name="GMV", line=dict(color="#f59e0b", width=3), fill='tozeroy', fillcolor='rgba(245, 158, 11, 0.08)'))
        fig.add_trace(go.Scatter(x=weekly["week"], y=weekly["marketplace_fee"], name="Net Revenue", line=dict(color="#10b981", width=2, dash="dot")))
        fig.update_layout(**get_plotly_layout("marketplace", height=320))
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        cat_agg = df.groupby("category")["amount"].sum().reset_index()
        fig_pie = px.pie(cat_agg, values="amount", names="category", hole=0.6, color_discrete_sequence=["#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6"])
        fig_pie.update_layout(**get_plotly_layout("marketplace", height=320))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    render_export_button(df[["order_id", "timestamp", "category", "amount", "status", "marketplace_fee"]].head(500), "marketplace_macro_summary.csv")
