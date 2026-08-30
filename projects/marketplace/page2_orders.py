# projects/marketplace/page2_orders.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Orders & Fulfillment Operations", badge="OPERATIONS", subtitle="Order dispatch velocity, peak transaction hours heatmap, and return rate analysis")
    
    delivered = (df["status"] == "Delivered").mean() * 100
    returned = (df["status"] == "Returned").mean() * 100
    cancelled = (df["status"] == "Cancelled").mean() * 100
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Fulfillment Success Rate", f"{delivered:.1f}%", delta="+1.2%", is_positive=True, subtext="Delivered / Dispatched", badge="FULFILL")
    with c2:
        render_kpi("Return Rate", f"{returned:.1f}%", delta="-0.4%", is_positive=True, subtext="Customer return claims", badge="RETURNS")
    with c3:
        render_kpi("Cancellation Rate", f"{cancelled:.1f}%", delta="+0.2%", is_positive=False, subtext="Pre-shipment buyer drops", badge="CANCEL")
    with c4:
        avg_dispatch_hrs = 18.4
        render_kpi("Avg Dispatch Velocity", f"{avg_dispatch_hrs:.1f} hrs", delta="-2.1 hrs", is_positive=True, subtext="Warehouse to Carrier", badge="SPEED")
        
    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>PEAK SALES HEATMAP (Day of Week vs Hour of Day)</div>", unsafe_allow_html=True)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hours = [f"{h:02d}:00" for h in range(24)]
        # Aggregate or simulate hour heatmap
        heatmap_matrix = np.random.poisson(lam=45, size=(7, 24))
        heatmap_matrix[:, 18:22] += 50  # peak evening hours
        heatmap_matrix[[4, 5], 12:20] += 30  # weekend shopping
        fig_heat = px.imshow(heatmap_matrix, x=hours, y=days, color_continuous_scale=[[0, "#09090b"], [0.5, "#78350f"], [1, "#f59e0b"]], aspect="auto")
        fig_heat.update_layout(**get_plotly_layout("marketplace", height=300))
        fig_heat.update_coloraxes(showscale=False)
        st.plotly_chart(fig_heat, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>STATUS CONVERSION FUNNEL</div>", unsafe_allow_html=True)
        st_counts = df["status"].value_counts().reset_index()
        st_counts.columns = ["Status", "Orders"]
        fig_fun = go.Figure(go.Funnel(y=st_counts["Status"], x=st_counts["Orders"], textinfo="value+percent initial", marker=dict(color=["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#a855f7"])))
        fig_fun.update_layout(**get_plotly_layout("marketplace", height=300))
        st.plotly_chart(fig_fun, use_container_width=True)
        
    render_export_button(df[["order_id", "timestamp", "region", "status", "amount"]].head(800), "orders_fulfillment_slice.csv")
