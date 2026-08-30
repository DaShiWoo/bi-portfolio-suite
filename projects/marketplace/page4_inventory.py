# projects/marketplace/page4_inventory.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout


def render(df_orders: pd.DataFrame):
    render_section_header(
        "Inventory Health & ABC/XYZ Matrix",
        badge="WAREHOUSING",
        subtitle="Stockout risk alerts, ABC distribution, SKU velocity, and Days of Inventory (DOI)",
    )

    # Load inventory data (not filtered by sidebar — warehouse data independent of order stream)
    df_inv = pd.read_parquet("data/marketplace_inventory.parquet")

    # ── Sidebar filters (for order-level cross-reference) ──────────────────────
    with st.sidebar:
        with st.expander("🔍 FILTERS", expanded=True):
            min_date = df_orders["timestamp"].dt.date.min()
            max_date = df_orders["timestamp"].dt.date.max()
            date_range = st.date_input("Date Range", value=[min_date, max_date])

            categories = st.multiselect(
                "Categories",
                options=df_orders["category"].unique().tolist(),
                default=df_orders["category"].unique().tolist(),
            )
            channels = st.multiselect(
                "Channels",
                options=df_orders["channel"].unique().tolist(),
                default=df_orders["channel"].unique().tolist(),
            )
            regions = st.multiselect(
                "Regions",
                options=df_orders["region"].unique().tolist(),
                default=df_orders["region"].unique().tolist(),
            )

    # Apply order filters for caption
    d0 = pd.to_datetime(date_range[0]) if len(date_range) >= 1 else pd.to_datetime(min_date)
    d1 = pd.to_datetime(date_range[1]) if len(date_range) >= 2 else pd.to_datetime(max_date)
    order_mask = (
        (df_orders["timestamp"] >= d0)
        & (df_orders["timestamp"] <= d1 + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
        & df_orders["category"].isin(categories)
        & df_orders["channel"].isin(channels)
        & df_orders["region"].isin(regions)
    )
    df_f = df_orders[order_mask]
    st.caption(f"Showing {len(df_f):,} of {len(df_orders):,} orders (inventory data: {len(df_inv)} SKUs)")

    # ── KPIs from inventory data ───────────────────────────────────────────────
    total_skus  = len(df_inv)
    crit_skus   = len(df_inv[df_inv["stockout_risk"] == "CRITICAL (< 7d)"])
    warn_skus   = len(df_inv[df_inv["days_of_inventory"] < 14])
    avg_doi     = df_inv["days_of_inventory"].mean()
    total_val   = (df_inv["stock_units"] * df_inv["unit_cost"]).sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Total Active SKUs", f"{total_skus}", delta=f"{warn_skus} at risk",
                   is_positive=warn_skus == 0, badge="SKUS")
    with c2:
        render_kpi("Critical OOS Alerts", f"{crit_skus} SKUs",
                   delta="< 7 days stock left",
                   is_positive=crit_skus == 0, subtext="Immediate restock needed", badge="STOCKOUT")
    with c3:
        render_kpi("Mean Days of Inventory", f"{avg_doi:.1f} days",
                   delta="Target: 25–45 days",
                   is_positive=25 <= avg_doi <= 45, subtext="Avg across all SKUs", badge="DOI")
    with c4:
        render_kpi("Warehouse Stock Value", f"${total_val:,.0f}", delta="+4.1% MoM",
                   is_positive=True, subtext="Cost basis valuation", badge="CAPITAL")

    # ── Row 2: ABC/XYZ matrix heatmap + ABC donut ──────────────────────────────
    c1, c2 = st.columns([6, 6])

    with c1:
        st.markdown(
            "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin-bottom:8px;'>ABC/XYZ CLASSIFICATION MATRIX (SKU Count)</div>",
            unsafe_allow_html=True,
        )
        matrix = df_inv.pivot_table(
            index="abc_class", columns="xyz_class",
            values="sku", aggfunc="count", fill_value=0,
        )
        fig_mat = px.imshow(
            matrix, text_auto=True,
            color_continuous_scale=[[0, "#09090b"], [0.5, "#78350f"], [1, "#f59e0b"]],
            aspect="auto",
        )
        fig_mat.update_layout(**get_plotly_layout("marketplace", height=300))
        fig_mat.update_coloraxes(showscale=False)
        st.plotly_chart(fig_mat, use_container_width=True)

    with c2:
        st.markdown(
            "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin-bottom:8px;'>ABC DISTRIBUTION — SKU Value Concentration</div>",
            unsafe_allow_html=True,
        )
        abc_counts = df_inv.groupby("abc_class").agg(
            sku_count=("sku", "count"),
            stock_val=("stock_units", "sum"),
        ).reset_index()
        fig_donut = px.pie(
            abc_counts, names="abc_class", values="stock_val", hole=0.55,
            color="abc_class",
            color_discrete_map={"A": "#f59e0b", "B": "#3b82f6", "C": "#6b7280"},
        )
        fig_donut.update_traces(textinfo="label+percent", textfont_size=13)
        fig_donut.update_layout(**get_plotly_layout("marketplace", height=300))
        st.plotly_chart(fig_donut, use_container_width=True)

    # ── Row 3: Stockout risk progress bars ────────────────────────────────────
    st.markdown(
        "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin:12px 0 8px;'>STOCKOUT RISK RADAR — SKUs with < 14 Days of Stock</div>",
        unsafe_allow_html=True,
    )
    crit_table = df_inv[df_inv["days_of_inventory"] < 14].sort_values("days_of_inventory").head(10)
    if len(crit_table) > 0:
        for _, row in crit_table.iterrows():
            doi   = max(0.0, float(row["days_of_inventory"]))
            frac  = min(doi / 14.0, 1.0)
            color = "#ef4444" if doi < 7 else "#f59e0b"
            col_a, col_b, col_c = st.columns([3, 5, 2])
            with col_a:
                st.markdown(
                    f"<span style='font-weight:600;color:#e4e4e7;font-size:0.85rem;'>{row['sku']}</span>"
                    f"<span style='color:#a1a1aa;font-size:0.8rem;'> ({row['category']})</span>",
                    unsafe_allow_html=True,
                )
            with col_b:
                st.progress(frac)
            with col_c:
                st.markdown(
                    f"<span style='color:{color};font-weight:700;font-size:0.88rem;'>{doi:.1f}d</span>"
                    f" <span style='color:#a1a1aa;font-size:0.75rem;'>{row['stockout_risk']}</span>",
                    unsafe_allow_html=True,
                )
    else:
        st.success("✅ No SKUs in critical stockout zone (< 14 days).")

    # ── Export ─────────────────────────────────────────────────────────────────
    render_export_button(df_inv, "inventory_abc_xyz_analysis.csv")
