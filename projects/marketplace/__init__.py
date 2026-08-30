# projects/marketplace/__init__.py
import streamlit as st
from core.data_loader import load_marketplace_orders
from projects.marketplace import page1_executive, page2_orders, page3_marketing, page4_inventory, page5_unit_econ

def render() -> None:
    df = load_marketplace_orders()
    
    tabs = st.tabs([
        "📊  1. Executive Macro Overview",
        "📦  2. Orders & Fulfillment Operations",
        "🎯  3. Marketing Attribution & ACoS",
        "🏬  4. Inventory & ABC/XYZ Matrix",
        "💰  5. Unit Economics & What-If"
    ])
    
    with tabs[0]:
        page1_executive.render(df)
    with tabs[1]:
        page2_orders.render(df)
    with tabs[2]:
        page3_marketing.render(df)
    with tabs[3]:
        page4_inventory.render(df)
    with tabs[4]:
        page5_unit_econ.render(df)
