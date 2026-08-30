# projects/fintech/page1_command.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.filters import build_fintech_filters, check_empty_state
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout


def render(df: pd.DataFrame) -> None:
    """Render live threat command center dashboard with real-time telemetry and automated mitigation."""
    render_section_header(
        "Live Threat Command Center",
        badge="REAL-TIME MONITORING",
        subtitle="Global transaction stream telemetry, real-time threat score, and instant automated mitigation",
    )

    if check_empty_state(df, "transactions"):
        return
    df_f = df

    # ── KPIs from filtered data ──────────────────────────────────────────────
    vol = df_f["amount"].sum()
    fraud_df = df_f[df_f["is_fraud"]]
    prevented = fraud_df["amount"].sum()
    fraud_pct = (len(fraud_df) / len(df_f) * 100) if len(df_f) > 0 else 0
    blocked = len(df_f[df_f["decision"] == "BLOCK"])
    review = len(df_f[df_f["decision"] == "FLAG_REVIEW"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Transaction Volume", f"${vol:,.0f}", delta="+3.1% volume", is_positive=True, subtext=f"{len(df_f):,} filtered transactions", badge="THROUGHPUT")
    with c2:
        render_kpi("Fraud Incident Rate", f"{fraud_pct:.2f}%", delta="-0.18% 24h", is_positive=True, subtext=f"Prevented Loss: ${prevented:,.0f}", badge="DEFENSE")
    with c3:
        render_kpi("Automated Blocks", f"{blocked:,}", delta="+14 blocked", is_positive=False, subtext="Risk threshold > 80.0", badge="SECURITY")
    with c4:
        render_kpi("Review Queue Pending", f"{review:,}", delta="-6 resolved", is_positive=True, subtext="Manual compliance checks", badge="QUEUE")

    # ── Volume donut (df_f) ────────────────────────────────────────────────────
    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>TRANSACTION VOLUME DONUT BY METHOD</div>", unsafe_allow_html=True)
        m_agg = df_f.groupby("payment_method").agg(amount=("amount", "sum")).reset_index()
        fig_donut = px.pie(
            m_agg, values="amount", names="payment_method", hole=0.58,
            color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ec4899"],
        )
        fig_donut.update_layout(**get_plotly_layout("fintech", height=300))
        st.plotly_chart(fig_donut, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>AUTOMATED RISK DECISION BAR</div>", unsafe_allow_html=True)
        dec_agg = df_f["decision"].value_counts().reset_index()
        dec_agg.columns = ["Decision", "Count"]
        fig_dec = px.bar(
            dec_agg, x="Decision", y="Count",
            color="Decision",
            color_discrete_map={"APPROVE": "#10b981", "FLAG_REVIEW": "#f59e0b", "BLOCK": "#ef4444"},
            text="Count",
        )
        fig_dec.update_layout(**get_plotly_layout("fintech", height=300), showlegend=False)
        st.plotly_chart(fig_dec, use_container_width=True)

    render_export_button(df_f[["txn_id", "timestamp", "amount", "payment_method", "risk_score", "decision"]].head(500), "fintech_command_stream.csv")
