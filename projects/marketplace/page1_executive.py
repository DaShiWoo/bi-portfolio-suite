# projects/marketplace/page1_executive.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout


def render(df: pd.DataFrame):
    render_section_header(
        "Executive Macro Performance",
        badge="MACRO OVERVIEW",
        subtitle="Top-line GMV, net revenue, take rate economics, and order fulfillment",
    )

    # ── Sidebar filters ────────────────────────────────────────────────────────
    with st.sidebar:
        with st.expander("🔍 FILTERS", expanded=True):
            min_date = df["timestamp"].dt.date.min()
            max_date = df["timestamp"].dt.date.max()
            date_range = st.date_input("Date Range", value=[min_date, max_date])

            categories = st.multiselect(
                "Categories",
                options=df["category"].unique().tolist(),
                default=df["category"].unique().tolist(),
            )
            channels = st.multiselect(
                "Channels",
                options=df["channel"].unique().tolist(),
                default=df["channel"].unique().tolist(),
            )
            regions = st.multiselect(
                "Regions",
                options=df["region"].unique().tolist(),
                default=df["region"].unique().tolist(),
            )

    # ── Apply filters ──────────────────────────────────────────────────────────
    d0 = pd.to_datetime(date_range[0]) if len(date_range) >= 1 else pd.to_datetime(min_date)
    d1 = pd.to_datetime(date_range[1]) if len(date_range) >= 2 else pd.to_datetime(max_date)
    mask = (
        (df["timestamp"] >= d0)
        & (df["timestamp"] <= d1 + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
        & df["category"].isin(categories)
        & df["channel"].isin(channels)
        & df["region"].isin(regions)
    )
    df_f = df[mask].copy()
    st.caption(f"Showing {len(df_f):,} of {len(df):,} orders")

    # ── KPIs ───────────────────────────────────────────────────────────────────
    gmv = df_f["amount"].sum()
    rev = df_f["marketplace_fee"].sum()
    take_rate = (rev / gmv * 100) if gmv > 0 else 0.0
    orders = len(df_f)
    aov = gmv / orders if orders > 0 else 0.0
    net_profit = df_f["profit"].sum()
    margin = (net_profit / rev * 100) if rev > 0 else 0.0

    # Real delta: first-half vs second-half of selected date range
    mid_ts = d0 + (d1 - d0) / 2
    gmv_h1 = df_f[df_f["timestamp"] < mid_ts]["amount"].sum()
    gmv_h2 = df_f[df_f["timestamp"] >= mid_ts]["amount"].sum()
    gmv_pct = ((gmv_h2 - gmv_h1) / gmv_h1 * 100) if gmv_h1 > 0 else 0.0
    rev_h1 = df_f[df_f["timestamp"] < mid_ts]["marketplace_fee"].sum()
    rev_h2 = df_f[df_f["timestamp"] >= mid_ts]["marketplace_fee"].sum()
    rev_pct = ((rev_h2 - rev_h1) / rev_h1 * 100) if rev_h1 > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi(
            "Gross Merchandise Value",
            f"${gmv:,.0f}",
            delta=f"{gmv_pct:+.1f}% H2 vs H1",
            is_positive=gmv_pct >= 0,
            subtext="Transaction runrate in period",
            badge="GMV",
        )
    with c2:
        render_kpi(
            "Net Marketplace Revenue",
            f"${rev:,.0f}",
            delta=f"{rev_pct:+.1f}% H2 vs H1",
            is_positive=rev_pct >= 0,
            subtext=f"Blended Take Rate: {take_rate:.1f}%",
            badge="REVENUE",
        )
    with c3:
        render_kpi(
            "Total Order Volume",
            f"{orders:,}",
            delta=f"AOV ${aov:.1f}",
            is_positive=True,
            subtext="Filtered order count",
            badge="ORDERS",
        )
    with c4:
        render_kpi(
            "Operating Net Margin",
            f"{margin:.1f}%",
            delta=f"Profit ${net_profit:,.0f}",
            is_positive=margin >= 0,
            subtext="Net Profit / Net Revenue",
            badge="MARGIN",
        )

    # ── Row 2: Weekly trend + sparkline overlay + treemap ─────────────────────
    c_left, c_right = st.columns([6, 6])

    with c_left:
        st.markdown(
            "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin-bottom:8px;'>GMV WEEKLY TREND + 4W SPARKLINE</div>",
            unsafe_allow_html=True,
        )
        ts = df_f.copy()
        ts["week"] = ts["timestamp"].dt.to_period("W").dt.to_timestamp()
        weekly = (
            ts.groupby("week")
            .agg({"amount": "sum", "marketplace_fee": "sum"})
            .reset_index()
        )
        weekly["gmv_ma4"] = weekly["amount"].rolling(4, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=weekly["week"],
                y=weekly["amount"],
                name="Weekly GMV",
                line=dict(color="#f59e0b", width=3),
                fill="tozeroy",
                fillcolor="rgba(245,158,11,0.08)",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=weekly["week"],
                y=weekly["marketplace_fee"],
                name="Net Revenue",
                line=dict(color="#10b981", width=2, dash="dot"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=weekly["week"],
                y=weekly["gmv_ma4"],
                name="4W MA",
                line=dict(color="#a78bfa", width=1.5, dash="dash"),
            )
        )
        fig.update_layout(**get_plotly_layout("marketplace", height=320))
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        st.markdown(
            "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin-bottom:8px;'>GMV SHARE BY CATEGORY (TREEMAP)</div>",
            unsafe_allow_html=True,
        )
        cat_agg = df_f.groupby("category")["amount"].sum().reset_index()
        cat_agg.columns = ["category", "gmv"]
        fig_tree = px.treemap(
            cat_agg,
            path=["category"],
            values="gmv",
            color="gmv",
            color_continuous_scale=["#1c1c1e", "#78350f", "#f59e0b"],
        )
        fig_tree.update_traces(textinfo="label+percent root", textfont_size=13)
        fig_tree.update_coloraxes(showscale=False)
        fig_tree.update_layout(**get_plotly_layout("marketplace", height=320))
        st.plotly_chart(fig_tree, use_container_width=True)

    # ── Export ─────────────────────────────────────────────────────────────────
    render_export_button(
        df_f[["order_id", "timestamp", "category", "channel", "region",
              "amount", "status", "marketplace_fee"]].head(500),
        "marketplace_macro_summary.csv",
    )
