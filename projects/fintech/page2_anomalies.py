# projects/fintech/page2_anomalies.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout
from core.filters import build_fintech_filters, check_empty_state


def render(df: pd.DataFrame) -> None:
    """Render the Anomaly Investigation & Risk Radar forensics page."""
    df_f = build_fintech_filters(df, key_prefix="fin_p2")
    if check_empty_state(df_f, "transactions"):
        return

    render_section_header(
        "Anomaly Investigation & Risk Radar",
        badge="FORENSICS",
        subtitle="Deep-dive into multi-variate statistical anomalies, outliers, and threshold triggers",
    )

    # ── KPIs from filtered data ──────────────────────────────────────────────
    anom_count = len(df_f[df_f["risk_score"] > 80])
    high_val = len(df_f[df_f["amount"] > 10000])
    proxy_pct = (df_f["proxy_ip"].mean() * 100) if len(df_f) > 0 else 0
    mean_score = df_f["risk_score"].mean() if len(df_f) > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("High-Score Anomalies", f"{anom_count:,}", delta="+18 detected", is_positive=False, badge="ANOMALIES")
    with c2:
        render_kpi("Whale Transactions (>$10k)", f"{high_val:,}", delta="Monitored transfers", is_positive=True, badge="WHALES")
    with c3:
        render_kpi("Proxy / VPN Usage", f"{proxy_pct:.1f}%", delta="+0.4% risk", is_positive=False, badge="NETWORK")
    with c4:
        render_kpi("Mean Anomaly Score", f"{mean_score:.1f} / 100", delta="-1.2 pts", is_positive=True, badge="BASELINE")

    # ── Scatter using df_f ─────────────────────────────────────────────────────
    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>ANOMALY SCATTER (AMOUNT VS RISK SCORE)</div>", unsafe_allow_html=True)
        sample = df_f.sample(min(1000, len(df_f))) if len(df_f) > 0 else df_f
        fig_sc = px.scatter(
            sample, x="amount", y="risk_score", color="decision",
            color_discrete_map={"APPROVE": "#10b981", "FLAG_REVIEW": "#f59e0b", "BLOCK": "#ef4444"},
            hover_data=["txn_id", "payment_method", "jurisdiction"],
        )
        fig_sc.add_hline(y=80, line_dash="dash", line_color="#ef4444", annotation_text="Auto-Block > 80")
        fig_sc.update_layout(**get_plotly_layout("fintech", height=320))
        st.plotly_chart(fig_sc, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>MULTI-VECTOR THREAT RADAR</div>", unsafe_allow_html=True)
        cats = ["Large Value", "Txn Velocity", "New Device", "High-Risk Geo", "Proxy/VPN", "Web3 Hop"]
        # Derive radar values from filtered data where possible
        large_val_score = min(100, high_val / max(len(df_f), 1) * 1000)
        vel_score = min(100, df_f["velocity_1h"].mean() * 20) if len(df_f) > 0 else 0
        proxy_score = min(100, proxy_pct * 2)
        anom_score = min(100, anom_count / max(len(df_f), 1) * 500)
        geo_risk = min(100, len(df_f[df_f["jurisdiction"].str.contains("Offshore|High-Risk", na=False)]) / max(len(df_f), 1) * 400)
        web3_fraud = min(100, len(df_f[(df_f["payment_method"] == "Web3/Crypto") & df_f["is_fraud"]]) / max(len(df_f), 1) * 800)

        fig_rad = go.Figure()
        fig_rad.add_trace(go.Scatterpolar(
            r=[large_val_score, vel_score, anom_score, geo_risk, proxy_score, web3_fraud],
            theta=cats, fill="toself",
            fillcolor="rgba(16,185,129,0.25)",
            line=dict(color="#10b981", width=2),
            name="Active Threat",
        ))
        fig_rad.add_trace(go.Scatterpolar(
            r=[35, 40, 30, 25, 20, 30],
            theta=cats, fill="toself",
            fillcolor="rgba(59,130,246,0.15)",
            line=dict(color="#3b82f6", width=1.5, dash="dot"),
            name="Baseline Norm",
        ))
        layout = get_plotly_layout("fintech", height=320)
        layout["polar"] = dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.08)"))
        fig_rad.update_layout(**layout)
        st.plotly_chart(fig_rad, use_container_width=True)

    render_export_button(df_f[df_f["risk_score"] > 75].head(500), "forensic_anomalies_export.csv")
