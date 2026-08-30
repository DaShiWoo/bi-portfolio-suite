# projects/marketplace/page3_marketing.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout


def render(df: pd.DataFrame):
    render_section_header(
        "Marketing Performance & Attribution",
        badge="ATTRIBUTION",
        subtitle="Paid campaigns efficiency, ACoS (ДРР), ROAS, channel CTR trend, and per-category attribution",
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

    # ── KPIs from df_f ─────────────────────────────────────────────────────────
    total_gmv  = df_f["amount"].sum()
    # Use take_rate column to estimate per-order ad attribution at 55% of fee
    est_ad_spend   = df_f["marketplace_fee"].sum() * 0.55
    blended_roas   = (total_gmv / est_ad_spend) if est_ad_spend > 0 else 0.0
    acos           = (est_ad_spend / total_gmv * 100) if total_gmv > 0 else 0.0
    avg_take_rate  = df_f["take_rate"].mean() * 100 if len(df_f) else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Total Ad Spend", f"${est_ad_spend:,.0f}", delta="55% of marketplace fee",
                   is_positive=False, subtext="Blended paid media est.", badge="SPEND")
    with c2:
        render_kpi("Blended ROAS", f"{blended_roas:.2f}x", delta=">3x target",
                   is_positive=blended_roas >= 3, subtext="GMV / Ad Spend", badge="ROAS")
    with c3:
        render_kpi("ACoS (ДРР)", f"{acos:.1f}%", delta="<15% target",
                   is_positive=acos < 15, subtext="Advertising Cost of Sales", badge="ACOS")
    with c4:
        render_kpi("Avg Take Rate", f"{avg_take_rate:.1f}%", delta=f"{len(df_f):,} orders",
                   is_positive=True, subtext="Mean platform take-rate", badge="TAKE")

    # ── Row 2: CTR trend line + channel scatter ────────────────────────────────
    c1, c2 = st.columns([6, 6])

    with c1:
        st.markdown(
            "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin-bottom:8px;'>CTR PROXY TREND — Weekly Revenue per Order (Est. Engagement)</div>",
            unsafe_allow_html=True,
        )
        if len(df_f) > 0:
            ts = df_f.copy()
            ts["week"] = ts["timestamp"].dt.to_period("W").dt.to_timestamp()
            ctr_trend = (
                ts.groupby(["week", "channel"])
                .agg(gmv=("amount", "sum"), cnt=("order_id", "count"))
                .reset_index()
            )
            ctr_trend["rev_per_order"] = ctr_trend["gmv"] / ctr_trend["cnt"]
            fig_ctr = px.line(
                ctr_trend, x="week", y="rev_per_order", color="channel",
                markers=True,
                color_discrete_sequence=["#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6"],
            )
            fig_ctr.update_layout(**get_plotly_layout("marketplace", height=320))
            st.plotly_chart(fig_ctr, use_container_width=True)
        else:
            st.info("No data in selected range.")

    with c2:
        st.markdown(
            "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin-bottom:8px;'>CHANNEL EFFICIENCY — Spend vs GMV (Bubble = Orders)</div>",
            unsafe_allow_html=True,
        )
        if len(df_f) > 0:
            chan_agg = (
                df_f.groupby("channel")
                .agg(gmv=("amount", "sum"), cnt=("order_id", "count"),
                     fee=("marketplace_fee", "sum"))
                .reset_index()
            )
            chan_agg["spend"] = chan_agg["fee"] * 0.55
            chan_agg["roas"]  = (chan_agg["gmv"] / chan_agg["spend"]).round(2)
            fig_scatter = px.scatter(
                chan_agg, x="spend", y="gmv", size="cnt", color="channel",
                text="channel", hover_data=["roas"],
                color_discrete_sequence=["#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6"],
            )
            fig_scatter.update_traces(textposition="top center")
            fig_scatter.update_layout(**get_plotly_layout("marketplace", height=320))
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No data in selected range.")

    # ── Row 3: Per-category ACoS table with color highlighting ────────────────
    st.markdown(
        "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin:12px 0 8px;'>PER-CATEGORY ACoS BREAKDOWN</div>",
        unsafe_allow_html=True,
    )
    if len(df_f) > 0:
        cat_agg = (
            df_f.groupby("category")
            .agg(gmv=("amount", "sum"), fee=("marketplace_fee", "sum"),
                 orders=("order_id", "count"), avg_take=("take_rate", "mean"))
            .reset_index()
        )
        cat_agg["ad_spend"] = cat_agg["fee"] * 0.55
        cat_agg["acos_pct"] = (cat_agg["ad_spend"] / cat_agg["gmv"] * 100).round(2)
        cat_agg["roas"]     = (cat_agg["gmv"] / cat_agg["ad_spend"]).round(2)
        cat_agg["avg_take_pct"] = (cat_agg["avg_take"] * 100).round(1)
        display = cat_agg[["category", "orders", "gmv", "ad_spend", "acos_pct", "roas", "avg_take_pct"]].copy()
        display.columns = ["Category", "Orders", "GMV ($)", "Ad Spend ($)", "ACoS (%)", "ROAS", "Avg Take Rate (%)"]
        display["GMV ($)"] = display["GMV ($)"].round(0)
        display["Ad Spend ($)"] = display["Ad Spend ($)"].round(0)

        def color_acos(val):
            if val < 12:
                return "color: #10b981; font-weight:700"
            elif val < 18:
                return "color: #f59e0b; font-weight:600"
            return "color: #ef4444; font-weight:700"

        def color_roas(val):
            if val >= 5:
                return "color: #10b981; font-weight:700"
            elif val >= 3:
                return "color: #f59e0b"
            return "color: #ef4444"

        styled = (
            display.style
            .applymap(color_acos, subset=["ACoS (%)"])
            .applymap(color_roas, subset=["ROAS"])
            .format({"GMV ($)": "${:,.0f}", "Ad Spend ($)": "${:,.0f}",
                     "ACoS (%)": "{:.1f}%", "ROAS": "{:.2f}x",
                     "Avg Take Rate (%)": "{:.1f}%"})
        )
        st.dataframe(styled, use_container_width=True, height=220)

    # ── Export ─────────────────────────────────────────────────────────────────
    if len(df_f) > 0:
        render_export_button(cat_agg, "marketing_category_acos.csv")
