# projects/saas/page4_cac.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    # ── Sidebar filters ──────────────────────────────────────────────────────
    with st.sidebar:
        with st.expander("🔍 FILTERS", expanded=True):
            tiers = st.multiselect(
                "Subscription Tier",
                options=df["tier"].unique().tolist(),
                default=df["tier"].unique().tolist(),
            )
            channels = st.multiselect(
                "Acquisition Channel",
                options=df["channel"].unique().tolist(),
                default=df["channel"].unique().tolist(),
            )
            churned_filter = st.radio(
                "Customer Status",
                ["All", "Active Only", "Churned Only"],
                index=0,
            )

    # ── Apply filters ────────────────────────────────────────────────────────
    df_f = df[df["tier"].isin(tiers) & df["channel"].isin(channels)]
    if churned_filter == "Active Only":
        df_f = df_f[~df_f["churned"]]
    elif churned_filter == "Churned Only":
        df_f = df_f[df_f["churned"]]

    render_section_header(
        "Customer Acquisition Cost & Payback Velocity",
        badge="UNIT ECONOMICS",
        subtitle="CAC by channel, months to recover acquisition spend, and LTV:CAC efficiency ratios",
    )

    # ── KPIs ─────────────────────────────────────────────────────────────────
    avg_cac = df_f["cac"].mean() if len(df_f) > 0 else 0
    active_df = df_f[~df_f["churned"]]
    arpu = active_df["mrr"].mean() if len(active_df) > 0 else 0
    payback_months = (avg_cac / arpu) if arpu > 0 else 0
    ltv = arpu * 28.0
    ltv_cac_ratio = (ltv / avg_cac) if avg_cac > 0 else 0
    inbound_share = (len(df_f[df_f["channel"] == "Inbound Organic"]) / len(df_f) * 100) if len(df_f) > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Blended CAC", f"${avg_cac:,.0f}", delta="-$180 vs budget", is_positive=True, subtext="Cost to acquire paying logo", badge="CAC")
    with c2:
        render_kpi("CAC Payback Period", f"{payback_months:.1f} months", delta="-1.2 mo", is_positive=payback_months <= 12, subtext="Target: < 12 months", badge="PAYBACK")
    with c3:
        render_kpi("LTV : CAC Ratio", f"{ltv_cac_ratio:.2f}x", delta="Top quartile > 3x", is_positive=ltv_cac_ratio >= 3, subtext=f"Estimated LTV: ${ltv:,.0f}", badge="EFFICIENCY")
    with c4:
        render_kpi("Inbound Channel Share", f"{inbound_share:.0f}%", delta="+5% YoY", is_positive=True, subtext="Lowest CAC acquisition vector", badge="INBOUND")

    # ── CAC vs LTV scatter per channel ──────────────────────────────────────
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>CAC vs LTV SCATTER PER CHANNEL</div>", unsafe_allow_html=True)
    scatter_df = df_f.copy()
    scatter_df["ltv"] = scatter_df["mrr"] * 28.0
    scatter_df["payback"] = (scatter_df["cac"] / scatter_df["mrr"].replace(0, float("nan"))).fillna(0)
    fig_sc = px.scatter(
        scatter_df.sample(min(800, len(scatter_df))),
        x="cac", y="ltv",
        color="channel",
        size="mrr",
        hover_data=["customer_id", "tier"],
        color_discrete_sequence=["#8b5cf6", "#38bdf8", "#10b981", "#f59e0b"],
        labels={"cac": "Customer Acquisition Cost ($)", "ltv": "Estimated LTV ($)"},
    )
    # Payback reference line: LTV = 3x CAC
    cac_range = [scatter_df["cac"].min(), scatter_df["cac"].max()]
    fig_sc.add_trace(go.Scatter(
        x=cac_range, y=[c * 3 for c in cac_range],
        mode="lines", line=dict(dash="dash", color="#ef4444", width=1.5),
        name="3x LTV:CAC Target",
    ))
    fig_sc.update_layout(**get_plotly_layout("saas", height=300))
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── Channel bar + payback ─────────────────────────────────────────────────
    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>CAC AND ARPU BY ACQUISITION CHANNEL</div>", unsafe_allow_html=True)
        chan_cac = df_f.groupby("channel").agg(cac=("cac", "mean"), mrr=("mrr", "mean")).reset_index()
        fig_bar = px.bar(
            chan_cac, x="channel", y=["cac", "mrr"], barmode="group",
            color_discrete_sequence=["#8b5cf6", "#38bdf8"],
        )
        fig_bar.update_layout(**get_plotly_layout("saas", height=280))
        st.plotly_chart(fig_bar, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>CAC PAYBACK TIMELINE — 12-MONTH TARGET LINE</div>", unsafe_allow_html=True)
        chan_cac["payback"] = (chan_cac["cac"] / chan_cac["mrr"].replace(0, float("nan"))).fillna(0).round(1)
        fig_p = px.bar(
            chan_cac, x="channel", y="payback",
            text=[f"{v:.1f}m" for v in chan_cac["payback"]],
            color="payback", color_continuous_scale=["#10b981", "#8b5cf6", "#ef4444"],
        )
        fig_p.add_hline(y=12, line_dash="dash", line_color="#38bdf8", annotation_text="12-month target")
        fig_p.update_layout(**get_plotly_layout("saas", height=280), coloraxis_showscale=False)
        st.plotly_chart(fig_p, use_container_width=True)

    render_export_button(chan_cac, "cac_channel_breakdown.csv")
