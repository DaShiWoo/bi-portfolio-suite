# projects/fintech/page5_simulator.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    # ── Sidebar filters ──────────────────────────────────────────────────────
    with st.sidebar:
        with st.expander("🔍 FILTERS", expanded=True):
            jurisdictions = st.multiselect(
                "Jurisdiction",
                options=df["jurisdiction"].unique().tolist(),
                default=df["jurisdiction"].unique().tolist(),
            )
            payment_methods = st.multiselect(
                "Payment Method",
                options=df["payment_method"].unique().tolist(),
                default=df["payment_method"].unique().tolist(),
            )
            risk_range = st.slider("Risk Score Range", 0, 100, (0, 100))

    # ── Apply filters ────────────────────────────────────────────────────────
    df_f = df[
        df["jurisdiction"].isin(jurisdictions)
        & df["payment_method"].isin(payment_methods)
        & (df["risk_score"] >= risk_range[0])
        & (df["risk_score"] <= risk_range[1])
    ]

    render_section_header(
        "Rule Engine Simulator & Precision Tuning",
        badge="WHAT-IF ENGINE",
        subtitle="Simulating precision vs recall trade-offs: false positive friction vs blocked fraud revenue",
    )

    st.markdown("""
    <div class="what-if-container">
        <span style="font-weight: 700; color: #10b981; font-size: 0.95rem;">🔮 INTERACTIVE WHAT-IF SCENARIO: AUTOMATED BLOCK THRESHOLD</span>
        <div style="font-size: 0.8rem; color: #6ee7b7; margin-top: 4px;">Adjust the automated block cutoff score to evaluate customer friction against fraud prevention:</div>
    </div>
    """, unsafe_allow_html=True)

    threshold = st.slider("Automated Block Cutoff Score", min_value=50.0, max_value=95.0, value=80.0, step=1.0)

    # Operate on df_f subset
    blocked_txns = df_f[df_f["risk_score"] >= threshold]
    true_fraud_blocked = blocked_txns[blocked_txns["is_fraud"]]
    false_positives = blocked_txns[~blocked_txns["is_fraud"]]
    fp_vol = false_positives["amount"].sum()
    precision = (len(true_fraud_blocked) / len(blocked_txns) * 100) if len(blocked_txns) > 0 else 100.0

    # ── KPIs ─────────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi("Fraud Volume Blocked", f"${true_fraud_blocked['amount'].sum():,.0f}", delta=f"{len(true_fraud_blocked)} attacks prevented", is_positive=True, badge="PREVENTED")
    with c2:
        render_kpi("False Positive Friction", f"${fp_vol:,.0f}", delta=f"{len(false_positives)} legit users blocked", is_positive=False, badge="FRICTION")
    with c3:
        render_kpi("Rule Precision Rate", f"{precision:.1f}%", delta="Target > 92%", is_positive=precision > 90, badge="PRECISION")

    # ── Waterfall: decision impact ────────────────────────────────────────────
    st.markdown(f"<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>SIMULATED DECISION WATERFALL AT CUTOFF = {threshold:.0f}</div>", unsafe_allow_html=True)
    fig_wf = go.Figure(go.Waterfall(
        name="Rule Impact", orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=["Total Transactions", "Approved Legit", "Legit Blocked (FP)", "Fraud Neutralized"],
        textposition="outside",
        y=[len(df_f), -(len(df_f) - len(blocked_txns)), -len(false_positives), len(true_fraud_blocked)],
        connector={"line": {"color": "rgba(255,255,255,0.2)"}},
        decreasing={"marker": {"color": "#3b82f6"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#ef4444"}},
    ))
    fig_wf.update_layout(**get_plotly_layout("fintech", height=320))
    st.plotly_chart(fig_wf, use_container_width=True)

    # ── df_f subset table preview ─────────────────────────────────────────────
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>FILTERED TRANSACTION SUBSET (TOP 200)</div>", unsafe_allow_html=True)
    subset_cols = ["txn_id", "amount", "payment_method", "jurisdiction", "risk_score", "decision", "is_fraud"]
    st.dataframe(
        df_f[subset_cols].sort_values("risk_score", ascending=False).head(200),
        use_container_width=True,
        height=280,
    )

    # ── Risk score distribution of filtered subset ────────────────────────────
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>RISK SCORE DISTRIBUTION (FILTERED SUBSET)</div>", unsafe_allow_html=True)
    fig_hist = px.histogram(
        df_f, x="risk_score", nbins=30, color="decision",
        color_discrete_map={"APPROVE": "#10b981", "FLAG_REVIEW": "#f59e0b", "BLOCK": "#ef4444"},
    )
    fig_hist.add_vline(x=threshold, line_dash="dash", line_color="#ffffff", annotation_text=f"Cutoff: {threshold:.0f}")
    fig_hist.update_layout(**get_plotly_layout("fintech", height=240))
    st.plotly_chart(fig_hist, use_container_width=True)

    render_export_button(
        pd.DataFrame([{
            "Cutoff": threshold,
            "Filtered_Txns": len(df_f),
            "Blocked_Fraud": len(true_fraud_blocked),
            "False_Positives": len(false_positives),
            "Precision": precision,
        }]),
        "threshold_simulation_results.csv",
    )
