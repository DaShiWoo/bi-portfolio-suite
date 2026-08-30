# projects/marketplace/page2_orders.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.filters import build_marketplace_filters, check_empty_state
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout


def render(df: pd.DataFrame) -> None:
    """Render orders and fulfillment operations dashboard with conversion funnels and peak hours."""
    render_section_header(
        "Orders & Fulfillment Operations",
        badge="OPERATIONS",
        subtitle="Order dispatch velocity, peak transaction hours heatmap, and channel breakdown",
    )

    if check_empty_state(df, "orders"):
        return
    df_f = df

    # ── KPIs (all from df_f) ───────────────────────────────────────────────────
    delivered_pct = (df_f["status"] == "Delivered").mean() * 100 if len(df_f) else 0.0
    returned_pct  = (df_f["status"] == "Returned").mean()  * 100 if len(df_f) else 0.0
    cancelled_pct = (df_f["status"] == "Cancelled").mean() * 100 if len(df_f) else 0.0
    shipped_pct   = (df_f["status"] == "Shipped").mean()   * 100 if len(df_f) else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Fulfillment Rate", f"{delivered_pct:.1f}%", delta=f"Shipped: {shipped_pct:.1f}%",
                   is_positive=True, subtext="Delivered / Dispatched", badge="FULFILL")
    with c2:
        render_kpi("Return Rate", f"{returned_pct:.1f}%", delta="Lower is better",
                   is_positive=returned_pct < 10, subtext="Customer return claims", badge="RETURNS")
    with c3:
        render_kpi("Cancellation Rate", f"{cancelled_pct:.1f}%", delta="Pre-shipment drops",
                   is_positive=cancelled_pct < 10, subtext="Buyer pre-shipment drops", badge="CANCEL")
    with c4:
        aov = df_f["amount"].mean() if len(df_f) else 0.0
        render_kpi("Avg Order Value", f"${aov:.1f}", delta=f"{len(df_f):,} orders",
                   is_positive=True, subtext="Mean basket size (filtered)", badge="AOV")

    # ── Row 2: Real heatmap + Channel breakdown bar ────────────────────────────
    c1, c2 = st.columns([6, 6])

    with c1:
        st.markdown(
            "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin-bottom:8px;'>PEAK SALES HEATMAP — Day of Week vs Hour</div>",
            unsafe_allow_html=True,
        )
        df_heat = df_f.copy()
        df_heat["dow"]  = df_heat["timestamp"].dt.dayofweek      # 0=Mon
        df_heat["hour"] = df_heat["timestamp"].dt.hour
        heat = (
            df_heat.groupby(["dow", "hour"])
            .size()
            .reset_index(name="orders")
        )
        heat_pivot = heat.pivot(index="dow", columns="hour", values="orders").fillna(0)
        # Ensure full 7×24 grid
        heat_pivot = heat_pivot.reindex(index=range(7), columns=range(24), fill_value=0)
        day_labels  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hour_labels = [f"{h:02d}:00" for h in range(24)]
        fig_heat = px.imshow(
            heat_pivot.values,
            x=hour_labels,
            y=day_labels,
            color_continuous_scale=[[0, "#09090b"], [0.5, "#78350f"], [1, "#f59e0b"]],
            aspect="auto",
        )
        fig_heat.update_layout(**get_plotly_layout("marketplace", height=300))
        fig_heat.update_coloraxes(showscale=False)
        st.plotly_chart(fig_heat, use_container_width=True)

    with c2:
        st.markdown(
            "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin-bottom:8px;'>CHANNEL BREAKDOWN — Orders & Revenue</div>",
            unsafe_allow_html=True,
        )
        ch_agg = (
            df_f.groupby("channel")
            .agg(orders=("order_id", "count"), revenue=("marketplace_fee", "sum"))
            .reset_index()
            .sort_values("revenue", ascending=False)
        )
        fig_ch = go.Figure()
        fig_ch.add_trace(go.Bar(
            y=ch_agg["channel"], x=ch_agg["revenue"],
            name="Net Revenue", orientation="h",
            marker_color="#f59e0b",
        ))
        fig_ch.add_trace(go.Bar(
            y=ch_agg["channel"], x=ch_agg["orders"],
            name="Order Count", orientation="h",
            marker_color="#10b981", visible="legendonly",
        ))
        fig_ch.update_layout(**get_plotly_layout("marketplace", height=300), barmode="overlay")
        st.plotly_chart(fig_ch, use_container_width=True)

    # ── Row 3: Status funnel ───────────────────────────────────────────────────
    st.markdown(
        "<div style='font-size:0.9rem;font-weight:600;color:#a1a1aa;margin:12px 0 8px;'>ORDER STATUS CONVERSION FUNNEL</div>",
        unsafe_allow_html=True,
    )
    st_counts = df_f["status"].value_counts().reset_index()
    st_counts.columns = ["Status", "Orders"]
    fig_fun = go.Figure(go.Funnel(
        y=st_counts["Status"], x=st_counts["Orders"],
        textinfo="value+percent initial",
        marker=dict(color=["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#a855f7"]),
    ))
    fig_fun.update_layout(**get_plotly_layout("marketplace", height=280))
    st.plotly_chart(fig_fun, use_container_width=True)

    # ── Export ─────────────────────────────────────────────────────────────────
    render_export_button(
        df_f[["order_id", "timestamp", "region", "channel", "status", "amount"]].head(800),
        "orders_fulfillment_slice.csv",
    )
