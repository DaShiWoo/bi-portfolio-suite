"""
hub.py
Master Entry Point for the Executive BI Portfolio Suite.
Showcases 6 complete production-grade BI dashboards (30 total analytics views):
- 🛍️ Marketplace & E-Commerce (Vercel Monochrome & Amber)
- ⚡ B2B SaaS & Subscriptions (Linear Dark & Stripe Royal Indigo)
- 🛡️ Fintech & Anti-Fraud Engine (Bloomberg Terminal & Emerald)
- 🎮 Game LiveOps & Economy (Cyber Neon Arcade)
- 🩺 HealthTech & Clinical Telemetry (Dark Teal & Mint Clinical)
- 🎧 Support Ops P&L — EverHelp / Zendesk Case (37k+ In-Memory Records)
"""
import streamlit as st
from core.theme import apply_theme

# Global Page Config
st.set_page_config(
    page_title="Executive BI Analytics Suite (25 Pages)",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Portfolio Navigation (Level 1)
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 14px;">
        <div style="font-size: 1.22rem; font-weight: 800; letter-spacing: -0.02em; color: #fff;">
            ⚡ ENTERPRISE BI SUITE
        </div>
        <div style="font-size: 0.76rem; color: #a1a1aa; margin-top: 4px;">
            6 Verticals • 30 Analytics Views • 37k+ In-Memory Records
        </div>
    </div>
    """, unsafe_allow_html=True)

    
    selected_project = st.radio(
        "SELECT VERTICAL / DOMAIN:",
        options=[
            "🛍️  Marketplace & Ads",
            "⚡  B2B SaaS Subscriptions",
            "🛡️  Fintech & Fraud Defense",
            "🎮  Game LiveOps & Economy",
            "🩺  HealthTech & Clinical Vitals",
            "🎧  Support Ops P&L (EverHelp / Zendesk Case)",
        ],
        index=0
    )

    
    st.markdown("""
    <div style="margin-top: 25px; padding: 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px;">
        <div style="font-size: 0.72rem; font-weight: 700; color: #a1a1aa; text-transform: uppercase;">Architecture & Stack</div>
        <div style="font-size: 0.76rem; color: #e4e4e7; margin-top: 6px; line-height: 1.5;">
            • <b>Total Pages:</b> 25 Full BI Views<br/>
            • <b>Engine:</b> DuckDB In-Memory OLAP<br/>
            • <b>Storage:</b> Apache Parquet (< 3MB)<br/>
            • <b>Interactivity:</b> What-If + CSV Export<br/>
            • <b>Design:</b> Custom Glassmorphism
        </div>
    </div>
    """, unsafe_allow_html=True)

# Route project and apply respective design language
if "Marketplace" in selected_project:
    apply_theme("marketplace")
    st.markdown("""
    <div style="margin-bottom: 14px;">
        <h1 style="font-size: 1.95rem; font-weight: 800; margin-bottom: 2px;">Marketplace & E-Commerce Intelligence</h1>
        <p style="color: #a1a1aa; font-size: 0.9rem; margin-top: 0;">GMV trajectory, take rate economics, order fulfillment funnels, inventory ABC/XYZ, and fee simulations</p>
    </div>
    """, unsafe_allow_html=True)
    from projects import marketplace
    marketplace.render()

elif "B2B SaaS" in selected_project:
    apply_theme("saas")
    st.markdown("""
    <div style="margin-bottom: 14px;">
        <h1 style="font-size: 1.95rem; font-weight: 800; margin-bottom: 2px; color: #f8fafc;">B2B SaaS & Subscriptions Intelligence</h1>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 0;">MRR/ARR growth velocity, Net Revenue Retention (NRR) cohorts, logo churn decomposition, CAC payback, and ARR forecast</p>
    </div>
    """, unsafe_allow_html=True)
    from projects import saas
    saas.render()

elif "Fintech" in selected_project:
    apply_theme("fintech")
    st.markdown("""
    <div style="margin-bottom: 14px;">
        <h1 style="font-size: 1.95rem; font-weight: 800; margin-bottom: 2px; color: #ecfdf5;">Fintech & Anti-Fraud Telemetry Command</h1>
        <p style="color: #6ee7b7; font-size: 0.9rem; margin-top: 0;">Real-time transaction stream, multi-vector risk radar, anomaly scatter, payment rails, and rule engine simulator</p>
    </div>
    """, unsafe_allow_html=True)
    from projects import fintech
    fintech.render()

elif "Game" in selected_project:
    apply_theme("gaming")
    st.markdown("""
    <div style="margin-bottom: 14px;">
        <h1 style="font-size: 1.95rem; font-weight: 800; margin-bottom: 2px; color: #f0fdfa;">Game LiveOps & Virtual Economy BI</h1>
        <p style="color: #a5f3fc; font-size: 0.9rem; margin-top: 0;">Player engagement DAU/MAU, level progression funnels, currency sink vs source, whale monetization, and D1/D7/D30 simulator</p>
    </div>
    """, unsafe_allow_html=True)
    from projects import gaming
    gaming.render()

elif "HealthTech" in selected_project:
    apply_theme("healthtech")
    st.markdown("""
    <div style="margin-bottom: 14px;">
        <h1 style="font-size: 1.95rem; font-weight: 800; margin-bottom: 2px; color: #f0fdf4;">HealthTech & Patient Biometrics Telemetry</h1>
        <p style="color: #99f6e4; font-size: 0.9rem; margin-top: 0;">Clinical ICU telemetry, ECG cardiovascular vitals density, Kaplan-Meier survival curves, risk stratification, and cohort explorer</p>
    </div>
    """, unsafe_allow_html=True)
    from projects import healthtech
    healthtech.render()

elif "Support Ops" in selected_project:
    from cases.support_ops_pnl.app import render as render_support_ops
    render_support_ops()

