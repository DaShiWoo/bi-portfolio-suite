# projects/fintech/page4_geo.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout
from core.filters import build_fintech_filters, check_empty_state


def render(df: pd.DataFrame) -> None:
    """Render the Cross-Border Geolocation Risk Matrix analytics page."""
    df_f = build_fintech_filters(df, key_prefix="fin_p4")
    if check_empty_state(df_f, "transactions"):
        return

    render_section_header(
        "Cross-Border Geolocation Risk Matrix",
        badge="JURISDICTIONS",
        subtitle="Tracking international settlement flows, high-risk territorial hubs, and sanction screening",
    )

    # ── Aggregate from filtered data ─────────────────────────────────────────
    geo_agg = df_f.groupby("jurisdiction").agg(
        volume=("amount", "sum"),
        txns=("txn_id", "count"),
        fraud_txns=("is_fraud", "sum"),
        mean_score=("risk_score", "mean"),
    ).reset_index()
    geo_agg["fraud_rate"] = (geo_agg["fraud_txns"] / geo_agg["txns"] * 100).round(2)

    # ── KPIs ─────────────────────────────────────────────────────────────────
    na_row = geo_agg[geo_agg["jurisdiction"] == "North America"]
    domestic_share = (na_row["volume"].values[0] / geo_agg["volume"].sum() * 100) if len(na_row) > 0 and geo_agg["volume"].sum() > 0 else 0
    offshore_row = geo_agg[geo_agg["jurisdiction"].str.contains("Offshore|High-Risk", na=False)]
    offshore_rate = offshore_row["fraud_rate"].values[0] if len(offshore_row) > 0 else 0
    cross_border_vol = df_f[df_f["jurisdiction"] != "North America"]["amount"].sum()
    block_ratio = (len(df_f[df_f["decision"] == "BLOCK"]) / len(df_f) * 100) if len(df_f) > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Domestic Traffic Share", f"{domestic_share:.1f}%", delta="Core safe volume", is_positive=True, badge="DOMESTIC")
    with c2:
        render_kpi("Offshore Fraud Rate", f"{offshore_rate:.1f}%", delta="Critical risk factor", is_positive=False, badge="OFFSHORE")
    with c3:
        render_kpi("Cross-Border Volume", f"${cross_border_vol:,.0f}", delta="+8.2%", is_positive=True, badge="GLOBAL")
    with c4:
        render_kpi("High-Risk Block Ratio", f"{block_ratio:.1f}%", delta="Automated perimeter", is_positive=True, badge="ENFORCE")

    # ── Volume donut + fraud rate bar ────────────────────────────────────────
    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>VOLUME CONTRIBUTION BY GEOGRAPHY</div>", unsafe_allow_html=True)
        fig_pie = px.pie(
            geo_agg, values="volume", names="jurisdiction", hole=0.55,
            color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ec4899", "#ef4444"],
        )
        fig_pie.update_layout(**get_plotly_layout("fintech", height=300))
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>FRAUD RATE BY JURISDICTION (%)</div>", unsafe_allow_html=True)
        fig_bar = px.bar(
            geo_agg.sort_values("fraud_rate", ascending=False),
            x="jurisdiction", y="fraud_rate",
            color="fraud_rate", color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
            text=[f"{v:.2f}%" for v in geo_agg.sort_values("fraud_rate", ascending=False)["fraud_rate"]],
        )
        fig_bar.update_layout(**get_plotly_layout("fintech", height=300), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Mean risk score by jurisdiction ─────────────────────────────────────
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>MEAN RISK SCORE BY JURISDICTION</div>", unsafe_allow_html=True)
    fig_risk = px.bar(
        geo_agg.sort_values("mean_score", ascending=False),
        x="jurisdiction", y="mean_score",
        color="mean_score", color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
        text=[f"{v:.1f}" for v in geo_agg.sort_values("mean_score", ascending=False)["mean_score"]],
    )
    fig_risk.add_hline(y=80, line_dash="dash", line_color="#ef4444", annotation_text="Auto-Block Threshold")
    fig_risk.update_layout(**get_plotly_layout("fintech", height=240), coloraxis_showscale=False)
    st.plotly_chart(fig_risk, use_container_width=True)

    render_export_button(geo_agg, "geolocation_risk_matrix.csv")
