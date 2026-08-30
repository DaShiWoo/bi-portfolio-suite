# projects/gaming/page4_monetization.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout
from core.filters import build_gaming_filters, check_empty_state


def render(df: pd.DataFrame) -> None:
    """Render the Monetization & Whale Economics analytics dashboard."""
    if check_empty_state(df, "players"):
        return
    df_f = df

    render_section_header(
        "Monetization & Whale Economics",
        badge="IAP REVENUE",
        subtitle="ARPPU, spender segment tiering, Battlepass conversion, and LTV distribution",
    )

    payers = df_f[df_f["iap_spend"] > 0]
    total_rev = df_f["iap_spend"].sum()
    payer_pct = (len(payers) / len(df_f) * 100) if len(df_f) > 0 else 0.0
    arppu = total_rev / len(payers) if len(payers) > 0 else 0.0
    whales = df_f[df_f["is_whale"]]
    whale_rev = whales["iap_spend"].sum()
    whale_rev_pct = (whale_rev / total_rev * 100) if total_rev > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Gross IAP Revenue", f"${total_rev:,.0f}", delta="+22.8% WoW", is_positive=True, badge="GROSS")
    with c2:
        render_kpi("Payer Conversion Rate", f"{payer_pct:.1f}%", delta="+0.6%", is_positive=True, subtext="Free-to-play conversion", badge="CONVERSION")
    with c3:
        render_kpi("Blended ARPPU", f"${arppu:.2f}", delta="+$3.40", is_positive=True, subtext="Avg revenue per paying user", badge="ARPPU")
    with c4:
        render_kpi("Whale Revenue Share", f"{whale_rev_pct:.1f}%", delta="Top 2.5% spenders", is_positive=True, subtext=f"${whale_rev:,.0f} whale IAP", badge="WHALES")

    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>SPENDER SEGMENT TIERING</div>", unsafe_allow_html=True)
        def classify_spender(val):
            if val == 0:
                return "Free Player ($0)"
            elif val < 10:
                return "Minnow ($1-$9)"
            elif val < 50:
                return "Dolphin ($10-$49)"
            else:
                return "Whale ($50+)"
        df_f_copy = df_f.copy()
        df_f_copy["spender_tier"] = df_f_copy["iap_spend"].apply(classify_spender)
        sp_agg = df_f_copy.groupby("spender_tier").agg(Revenue=("iap_spend", "sum"), Players=("player_id", "count")).reset_index()
        fig_b = px.bar(
            sp_agg, x="spender_tier", y="Revenue", color="spender_tier",
            color_discrete_sequence=["#06b6d4", "#38bdf8", "#c084fc", "#ec4899"],
            text="Players",
        )
        fig_b.update_traces(texttemplate="%{text} players", textposition="outside")
        fig_b.update_layout(**get_plotly_layout("gaming", height=300), showlegend=False)
        st.plotly_chart(fig_b, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>BATTLEPASS TIER COMPLETION</div>", unsafe_allow_html=True)
        bp_labels = ["Tier 1-20", "Tier 21-50", "Tier 51-80", "Max Tier (100)"]
        bp_series = pd.cut(df_f["battlepass_tier"], bins=[0, 20, 50, 80, 100], labels=bp_labels)
        bp_agg = bp_series.value_counts().reindex(bp_labels).fillna(0).reset_index()
        bp_agg.columns = ["Tier", "Players"]
        fig_pie = px.pie(
            bp_agg, values="Players", names="Tier", hole=0.6,
            color_discrete_sequence=["#06b6d4", "#ec4899", "#a855f7", "#10b981"],
        )
        fig_pie.update_layout(**get_plotly_layout("gaming", height=300))
        st.plotly_chart(fig_pie, use_container_width=True)

    export_df = whales[["player_id", "level", "iap_spend", "gold_balance", "channel"]] if len(whales) > 0 else df_f[["player_id", "level", "iap_spend", "gold_balance", "channel"]].head(0)
    render_export_button(export_df, "whale_segment_export.csv")
