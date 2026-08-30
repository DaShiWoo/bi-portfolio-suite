# projects/gaming/page3_currency.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    # ── Sidebar Filters ───────────────────────────────────────────────────────
    with st.sidebar:
        with st.expander("🔍 FILTERS", expanded=True):
            channels = st.multiselect(
                "Acquisition Channel",
                options=df["channel"].unique().tolist(),
                default=df["channel"].unique().tolist(),
            )
            level_range = st.slider("Player Level Range", 1, 50, (1, 50))
            payers_only = st.checkbox("Paying Players Only", value=False)

    df_f = df[df["channel"].isin(channels) & df["level"].between(level_range[0], level_range[1])].copy()
    if payers_only:
        df_f = df_f[df_f["iap_spend"] > 0]

    render_section_header(
        "Virtual Currency Economy: Sink vs Source",
        badge="MACRO ECONOMY",
        subtitle="Monitoring money supply, gold faucet sources, item sinks, and currency velocity",
    )

    total_gold = df_f["gold_balance"].sum()
    mean_gold = df_f["gold_balance"].mean() if len(df_f) > 0 else 0.0
    median_gold = df_f["gold_balance"].median() if len(df_f) > 0 else 0.0
    zero_gold = (df_f["gold_balance"] == 0).sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Circulating Gold Pool", f"{total_gold/1e6:.2f}M Gold", delta="+4.2% MoM", is_positive=True, badge="SUPPLY")
    with c2:
        render_kpi("Sink / Source Ratio", "0.94x", delta="Stable balance (~1.0x)", is_positive=True, badge="RATIO")
    with c3:
        render_kpi("Mean Gold Per Active", f"{mean_gold:,.0f}", delta=f"Median: {median_gold:,.0f}", is_positive=True, badge="PER CAPITA")
    with c4:
        render_kpi("Zero-Balance Players", f"{zero_gold:,}", delta="Currency depleted", is_positive=False, badge="DEPLETED")

    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>GOLD BALANCE DISTRIBUTION</div>", unsafe_allow_html=True)
        fig_hist = px.histogram(
            df_f, x="gold_balance", nbins=40,
            color_discrete_sequence=["#06b6d4"],
            labels={"gold_balance": "Gold Balance"},
        )
        fig_hist.update_layout(**get_plotly_layout("gaming", height=300))
        st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>GOLD BALANCE BY ACQUISITION CHANNEL</div>", unsafe_allow_html=True)
        fig_box = px.box(
            df_f, x="channel", y="gold_balance", color="channel",
            color_discrete_sequence=["#06b6d4", "#ec4899", "#a855f7", "#10b981", "#f59e0b"],
            points=False,
        )
        fig_box.update_layout(**get_plotly_layout("gaming", height=300), showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    render_export_button(df_f[["player_id", "level", "gold_balance", "iap_spend"]].head(500), "virtual_economy_ledger.csv")
