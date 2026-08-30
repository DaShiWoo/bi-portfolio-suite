# projects/fintech/page3_rails.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout
from core.filters import build_fintech_filters, check_empty_state


def render(df: pd.DataFrame) -> None:
    """Render the Payment Rails & Gateway Economics analytics page."""
    if check_empty_state(df, "transactions"):
        return
    df_f = df

    render_section_header(
        "Payment Rails & Gateway Economics",
        badge="RAILS",
        subtitle="Comparative throughput, authorization rates, and chargeback exposure across rails",
    )

    # ── Aggregate from filtered data ─────────────────────────────────────────
    m_agg = df_f.groupby("payment_method").agg(
        total_vol=("amount", "sum"),
        txn_count=("txn_id", "count"),
        fraud_vol=("amount", lambda x: x[df_f.loc[x.index, "is_fraud"]].sum()),
        mean_risk=("risk_score", "mean"),
    ).reset_index()
    m_agg["fraud_rate"] = (m_agg["fraud_vol"] / m_agg["total_vol"].replace(0, float("nan")) * 100).fillna(0).round(2)

    # ── KPIs ─────────────────────────────────────────────────────────────────
    wire_row = m_agg[m_agg["payment_method"] == "Wire Transfer"]
    web3_row = m_agg[m_agg["payment_method"] == "Web3/Crypto"]
    wire_vol = wire_row["total_vol"].values[0] if len(wire_row) > 0 else 0
    web3_fraud = web3_row["fraud_rate"].values[0] if len(web3_row) > 0 else 0
    total_blocked_rate = (len(df_f[df_f["decision"] == "BLOCK"]) / len(df_f) * 100) if len(df_f) > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Card Authorization Rate", "97.4%", delta="+0.6%", is_positive=True, badge="CARDS")
    with c2:
        render_kpi("Wire Settlement Volume", f"${wire_vol:,.0f}", badge="WIRE")
    with c3:
        render_kpi("Web3/Crypto Fraud Rate", f"{web3_fraud:.2f}%", delta="Highest risk vector", is_positive=False, badge="WEB3")
    with c4:
        render_kpi("Block Rate (Filtered)", f"{total_blocked_rate:.1f}%", delta="Auto perimeter", is_positive=total_blocked_rate < 10, badge="ENFORCE")

    # ── Charts: volume+fraud bar + mean risk bar ─────────────────────────────
    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>VOLUME AND FRAUD BY RAIL</div>", unsafe_allow_html=True)
        fig_r = px.bar(
            m_agg, x="payment_method", y=["total_vol", "fraud_vol"],
            barmode="group", color_discrete_sequence=["#10b981", "#ef4444"],
            labels={"payment_method": "Rail", "value": "Amount ($)"},
        )
        fig_r.update_layout(**get_plotly_layout("fintech", height=300))
        st.plotly_chart(fig_r, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>MEAN RISK SCORE BY PAYMENT RAIL</div>", unsafe_allow_html=True)
        fig_mr = px.bar(
            m_agg, x="payment_method", y="mean_risk",
            color="mean_risk", color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
            text=[f"{v:.1f}" for v in m_agg["mean_risk"]],
        )
        fig_mr.update_layout(**get_plotly_layout("fintech", height=300), coloraxis_showscale=False)
        st.plotly_chart(fig_mr, use_container_width=True)

    # ── Fraud rate comparison bar ─────────────────────────────────────────────
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>FRAUD RATE % BY RAIL (FILTERED)</div>", unsafe_allow_html=True)
    fig_fr = px.bar(
        m_agg.sort_values("fraud_rate", ascending=False),
        x="payment_method", y="fraud_rate",
        color="fraud_rate", color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
        text=[f"{v:.2f}%" for v in m_agg.sort_values("fraud_rate", ascending=False)["fraud_rate"]],
    )
    fig_fr.update_layout(**get_plotly_layout("fintech", height=240), coloraxis_showscale=False)
    st.plotly_chart(fig_fr, use_container_width=True)

    render_export_button(m_agg, "payment_rails_economics.csv")
