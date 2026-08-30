# projects/marketplace/page5_unit_econ.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout


def render(df: pd.DataFrame):
    render_section_header(
        "Unit Economics & What-If Fee Simulator",
        badge="PROFITABILITY",
        subtitle="Waterfall margin breakdown from real data, LTV dynamics, and interactive fee modeling",
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

    # ── Real unit econ derived from df_f ───────────────────────────────────────
    total_gmv    = df_f["amount"].sum()
    total_fee    = df_f["marketplace_fee"].sum()
    total_cogs   = df_f["cogs"].sum()
    total_profit = df_f["profit"].sum()
    orders       = len(df_f)
    avg_gmv      = total_gmv  / orders if orders > 0 else 0.0
    avg_fee      = total_fee  / orders if orders > 0 else 0.0
    avg_cogs     = total_cogs / orders if orders > 0 else 0.0
    avg_profit   = total_profit / orders if orders > 0 else 0.0
    avg_take     = df_f["take_rate"].mean() * 100 if orders > 0 else 0.0

    # Seller payout per order = avg_gmv - avg_fee
    avg_seller_payout = avg_gmv - avg_fee
    # Payment gateway estimate: 2.5% of GMV
    avg_gateway = avg_gmv * 0.025
    # Platform ops: remainder after fee & gateway & cogs cover
    avg_ops     = avg_fee * 0.23   # ~23% of fee goes to platform ops
    avg_net_contrib = avg_fee - avg_gateway - avg_ops

    # ── What-If Simulator ──────────────────────────────────────────────────────
    st.markdown(
        """<div class="what-if-container">
            <span style="font-weight:700;color:#f59e0b;font-size:0.95rem;">🔮 INTERACTIVE WHAT-IF: COMMISSION FEE ADJUSTMENT</span>
            <div style="font-size:0.8rem;color:#a1a1aa;margin-top:4px;">
                Simulate net revenue impact of altering marketplace take-rate — computed on filtered GMV
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    sim_take_rate = st.slider(
        "Simulated Marketplace Take Rate (%)",
        min_value=8.0, max_value=25.0,
        value=float(round(avg_take, 1)), step=0.2,
    )

    sim_rev   = total_gmv * (sim_take_rate / 100.0)
    actual_rev = total_fee
    rev_delta  = sim_rev - actual_rev

    # CAC & LTV rough estimates from order data
    est_cac = avg_cogs * 0.18   # 18% of avg COGS as CAC proxy
    est_ltv = avg_profit * 4.2  # 12-month repeat purchase factor

    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi("Simulated Net Revenue", f"${sim_rev:,.0f}",
                   delta=f"{rev_delta:+,.0f} vs actual",
                   is_positive=rev_delta >= 0, badge="SIMULATED")
    with c2:
        render_kpi("Est. Customer Acq. Cost", f"${est_cac:.2f}",
                   delta=f"LTV:CAC {est_ltv/est_cac:.1f}x" if est_cac > 0 else "N/A",
                   is_positive=est_ltv / est_cac >= 3 if est_cac > 0 else True, badge="CAC")
    with c3:
        render_kpi("Est. 12M LTV", f"${est_ltv:.2f}",
                   delta=f"Avg Profit ${avg_profit:.2f}/order",
                   is_positive=True, badge="LTV")

    # ── Cost Waterfall from real df_f numbers ─────────────────────────────────
    render_section_header("Per-Order Unit Economic Waterfall (Real Data)", badge="WATERFALL")

    if orders > 0:
        labels = [
            "Buyer Payment (GMV)",
            f"Seller Payout ({100 - avg_take:.1f}%)",
            "Payment Gateway (2.5%)",
            f"Platform Ops ({avg_ops/avg_fee*100:.1f}% of fee)" if avg_fee > 0 else "Platform Ops",
            "Net Contribution",
        ]
        values = [
            avg_gmv,
            -avg_seller_payout,
            -avg_gateway,
            -avg_ops,
            0.0,  # total placeholder
        ]
        texts = [
            f"+${avg_gmv:.2f}",
            f"-${avg_seller_payout:.2f}",
            f"-${avg_gateway:.2f}",
            f"-${avg_ops:.2f}",
            f"${avg_net_contrib:.2f}",
        ]
        fig_wf = go.Figure(go.Waterfall(
            name="Unit Margin",
            orientation="v",
            measure=["relative", "relative", "relative", "relative", "total"],
            x=labels,
            textposition="outside",
            text=texts,
            y=values,
            connector={"line": {"color": "rgba(255,255,255,0.2)"}},
            decreasing={"marker": {"color": "#ef4444"}},
            increasing={"marker": {"color": "#10b981"}},
            totals={"marker": {"color": "#f59e0b"}},
        ))
        fig_wf.update_layout(**get_plotly_layout("marketplace", height=340))
        st.plotly_chart(fig_wf, use_container_width=True)

        # ── Per-category waterfall comparison ─────────────────────────────────
        st.markdown(
            "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin:12px 0 8px;'>NET CONTRIBUTION MARGIN BY CATEGORY</div>",
            unsafe_allow_html=True,
        )
        cat_econ = (
            df_f.groupby("category")
            .agg(gmv=("amount", "sum"), fee=("marketplace_fee", "sum"),
                 cogs=("cogs", "sum"), profit=("profit", "sum"),
                 orders=("order_id", "count"))
            .reset_index()
        )
        cat_econ["net_margin_pct"] = (cat_econ["profit"] / cat_econ["gmv"] * 100).round(1)
        cat_econ["take_rate_pct"]  = (cat_econ["fee"] / cat_econ["gmv"] * 100).round(1)
        cat_econ["simulated_fee"]  = cat_econ["gmv"] * (sim_take_rate / 100.0)
        cat_econ["sim_delta"]      = cat_econ["simulated_fee"] - cat_econ["fee"]

        fig_cat = px.bar(
            cat_econ.sort_values("net_margin_pct", ascending=True),
            x="net_margin_pct", y="category", orientation="h",
            color="net_margin_pct",
            color_continuous_scale=["#ef4444", "#78350f", "#f59e0b", "#10b981"],
            text="net_margin_pct",
        )
        fig_cat.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_cat.update_coloraxes(showscale=False)
        fig_cat.update_layout(**get_plotly_layout("marketplace", height=280))
        st.plotly_chart(fig_cat, use_container_width=True)

    else:
        st.info("No data in selected range to compute waterfall.")

    # ── Export ─────────────────────────────────────────────────────────────────
    export_df = pd.DataFrame([{
        "Base GMV": total_gmv,
        "Actual Revenue": actual_rev,
        "Simulated Take Rate (%)": sim_take_rate,
        "Simulated Revenue": sim_rev,
        "Revenue Delta": rev_delta,
        "Avg GMV/Order": avg_gmv,
        "Avg Fee/Order": avg_fee,
        "Avg COGS/Order": avg_cogs,
        "Avg Profit/Order": avg_profit,
    }])
    render_export_button(export_df, "scenario_modeling_export.csv")
