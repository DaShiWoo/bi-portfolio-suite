"""
hub.py
Master Entry Point for the Executive BI Portfolio Suite.
Showcases 6 complete production-grade BI dashboards (30 total analytics views):
- 🛍️ Marketplace & E-Commerce (Vercel Monochrome & Amber)
- ⚡ B2B SaaS & Subscriptions (Linear Dark & Stripe Royal Indigo)
- 🛡️ Fintech & Anti-Fraud Engine (Bloomberg Terminal & Emerald)
- 🎮 Game LiveOps & Economy (Cyber Neon Arcade)
- 🩺 HealthTech & Patient Biometrics (ICU, Kaplan-Meier, Risk Scoring)
- 🎧 Support Ops P&L — Zendesk Benchmark Case (37k+ In-Memory Records)
"""
import streamlit as st
from core.theme import apply_theme, render_page_header

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
            "🎧  Support Ops P&L (Zendesk Benchmark Case)",
        ],
        index=0
    )

    
    st.markdown("""
    <div style="margin-top: 24px; margin-bottom: 22px; padding: 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px;">
        <div style="font-size: 0.72rem; font-weight: 700; color: #a1a1aa; text-transform: uppercase; letter-spacing: 0.05em;">Architecture & Stack</div>
        <div style="font-size: 0.76rem; color: #e4e4e7; margin-top: 6px; line-height: 1.55;">
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
    render_page_header(
        title="Marketplace & E-Commerce Intelligence",
        subtitle="GMV trajectory, take rate economics, order fulfillment funnels, inventory ABC/XYZ, and fee simulations",
        theme_key="marketplace"
    )
    from projects import marketplace
    marketplace.render()

elif "B2B SaaS" in selected_project:
    apply_theme("saas")
    render_page_header(
        title="B2B SaaS & Subscriptions Intelligence",
        subtitle="MRR/ARR growth velocity, Net Revenue Retention (NRR) cohorts, logo churn decomposition, CAC payback, and ARR forecast",
        theme_key="saas"
    )
    from projects import saas
    saas.render()

elif "Fintech" in selected_project:
    apply_theme("fintech")
    render_page_header(
        title="Fintech & Anti-Fraud Telemetry Command",
        subtitle="Real-time transaction stream, multi-vector risk radar, anomaly scatter, payment rails, and rule engine simulator",
        theme_key="fintech"
    )
    from projects import fintech
    fintech.render()

elif "Game" in selected_project:
    apply_theme("gaming")
    render_page_header(
        title="Game LiveOps & Virtual Economy BI",
        subtitle="Player engagement DAU/MAU, level progression funnels, currency sink vs source, whale monetization, and D1/D7/D30 simulator",
        theme_key="gaming"
    )
    from projects import gaming
    gaming.render()

elif "HealthTech" in selected_project:
    apply_theme("healthtech")
    render_page_header(
        title="HealthTech & Patient Biometrics Telemetry",
        subtitle="Clinical ICU telemetry, ECG cardiovascular vitals density, Kaplan-Meier survival curves, risk stratification, and cohort explorer",
        theme_key="healthtech"
    )
    from projects import healthtech
    healthtech.render()

elif "Support Ops" in selected_project:
    import importlib
    import cases.support_ops_pnl.app as support_ops_module
    importlib.reload(support_ops_module)
    support_ops_module.render()



