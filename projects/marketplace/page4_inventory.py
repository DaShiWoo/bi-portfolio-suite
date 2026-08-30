# projects/marketplace/page4_inventory.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df_orders):
    render_section_header("Inventory Health & ABC/XYZ Matrix", badge="WAREHOUSING", subtitle="Stockout risk alerts, SKU velocity, and Days of Inventory (DOI)")
    
    df_inv = pd.read_parquet("data/marketplace_inventory.parquet")
    
    total_skus = len(df_inv)
    crit_skus = len(df_inv[df_inv["stockout_risk"] == "CRITICAL (< 7d)"])
    avg_doi = df_inv["days_of_inventory"].mean()
    total_val = (df_inv["stock_units"] * df_inv["unit_cost"]).sum()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Total Active SKUs", f"{total_skus}", delta="120 catalogue items", is_positive=True, badge="SKUS")
    with c2:
        render_kpi("Critical OOS Alerts", f"{crit_skus} SKUs", delta="-3 items", is_positive=False, subtext="Stockout risk < 7 days", badge="STOCKOUT")
    with c3:
        render_kpi("Mean Days of Inventory", f"{avg_doi:.1f} days", delta="+2.4 days", is_positive=True, subtext="Target range: 25 - 45d", badge="DOI")
    with c4:
        render_kpi("Warehouse Stock Value", f"${total_val:,.0f}", delta="+4.1%", is_positive=True, subtext="Cost basis valuation", badge="CAPITAL")
        
    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>ABC/XYZ CLASSIFICATION MATRIX</div>", unsafe_allow_html=True)
        matrix = df_inv.pivot_table(index="abc_class", columns="xyz_class", values="sku", aggfunc="count", fill_value=0)
        fig_mat = px.imshow(matrix, text_auto=True, color_continuous_scale=[[0, "#09090b"], [0.5, "#78350f"], [1, "#f59e0b"]], aspect="auto")
        fig_mat.update_layout(**get_plotly_layout("marketplace", height=300))
        fig_mat.update_coloraxes(showscale=False)
        st.plotly_chart(fig_mat, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>CRITICAL RESTOCK RADAR (< 14 DAYS STOCK)</div>", unsafe_allow_html=True)
        crit_table = df_inv[df_inv["days_of_inventory"] < 14].sort_values("days_of_inventory")
        st.dataframe(crit_table[["sku", "category", "stock_units", "daily_velocity", "days_of_inventory", "stockout_risk"]], use_container_width=True, height=265)
        
    render_export_button(df_inv, "inventory_abc_xyz_analysis.csv")
