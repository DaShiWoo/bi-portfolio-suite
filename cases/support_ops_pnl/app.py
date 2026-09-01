"""
cases/support_ops_pnl/app.py
Executive Premium Dashboard: Zendesk в†’ DuckDB OLAP Cohorts в†’ P&L
C-Level / Head of Delivery вЂ” 300+ FTE

Public API:
  render() вЂ” embed in hub.py or any Streamlit host (no set_page_config called).
  main()   вЂ” standalone entry point (calls set_page_config + render).
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from cases.support_ops_pnl.db_engine import (
    get_connection,
    get_executive_kpis,
    get_cohort_retention_matrix,
    get_tier_pnl_breakdown,
    get_channel_metrics,
    simulate_margin_sensitivity,
)


# в”Ђв”Ђ Premium CSS в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800&display=swap" rel="stylesheet">

<style>
/* в”Ђв”Ђ Reset & Base в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #070B14 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: #E2E8F0;
    -webkit-font-smoothing: antialiased;
}

/* в”Ђв”Ђ Hide Streamlit chrome в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.stDeployButton { display: none; }

/* в”Ђв”Ђ Layout в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
.main > div { padding: 0 !important; }

/* в”Ђв”Ђ Custom scrollbar в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #070B14; }
::-webkit-scrollbar-thumb { background: #1E3A5F; border-radius: 4px; }

/* в”Ђв”Ђ Page wrapper в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
.page-wrap {
    padding: 28px 36px 60px 36px;
    max-width: 1440px;
    margin: 0 auto;
}

/* в”Ђв”Ђ Top nav bar в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 24px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 28px;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 12px;
}
.nav-logo-mark {
    width: 34px;
    height: 34px;
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 20px rgba(37,99,235,0.35);
}
.nav-logo-mark svg { width: 18px; height: 18px; }
.nav-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #F1F5F9;
    letter-spacing: -0.01em;
}
.nav-sub {
    font-size: 0.72rem;
    color: #334155;
    font-weight: 400;
    margin-top: 1px;
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(37, 99, 235, 0.08);
    border: 1px solid rgba(37, 99, 235, 0.18);
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.70rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #60A5FA;
}
.pulse {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #22D3EE;
    animation: blink 2s ease infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:.25;} }
.pill-neutral {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.70rem;
    font-weight: 500;
    color: #475569;
}

/* в”Ђв”Ђ KPI Cards в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 32px;
}
.kpi {
    background: #0C1220;
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 14px;
    padding: 22px 22px 18px 22px;
    position: relative;
    overflow: hidden;
    transition: border-color .25s, box-shadow .25s;
    cursor: default;
}
.kpi:hover {
    border-color: rgba(255,255,255,0.10);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi::after {
    content: "";
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 60px;
    background: linear-gradient(to top, var(--glow, rgba(37,99,235,0.04)), transparent);
    pointer-events: none;
}
.kpi-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}
.kpi-tag {
    font-size: 0.675rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #334155;
}
.kpi-badge {
    font-size: 0.65rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 10px;
    letter-spacing: 0.04em;
}
.kpi-num {
    font-size: 2.15rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 10px;
}
.kpi-foot {
    font-size: 0.725rem;
    color: #2D3E55;
    font-weight: 400;
    line-height: 1.5;
    border-top: 1px solid rgba(255,255,255,0.04);
    padding-top: 10px;
    margin-top: 2px;
}
.kpi-foot strong { color: #3D5470; font-weight: 600; }
.kpi-accent-bar {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent-color, #2563EB);
    border-radius: 14px 14px 0 0;
}

/* в”Ђв”Ђ Section separator в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
.sec {
    margin: 0 0 14px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}
.sec-icon {
    width: 30px; height: 30px;
    background: #0C1220;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.sec-icon svg { width: 14px; height: 14px; }
.sec-text { flex: 1; }
.sec-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #CBD5E1;
    letter-spacing: -0.01em;
}
.sec-desc {
    font-size: 0.72rem;
    color: #263347;
    font-weight: 400;
    margin-top: 1px;
}
.sec-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, rgba(255,255,255,0.05), transparent);
}

/* в”Ђв”Ђ Insight Callout в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
.insight {
    background: rgba(12, 18, 32, 0.85);
    border: 1px solid rgba(255,255,255,0.05);
    border-left: 2px solid var(--accent-color, #2563EB);
    border-radius: 0 8px 8px 0;
    padding: 11px 14px;
    font-size: 0.78rem;
    color: #2D4A6A;
    line-height: 1.65;
    margin-top: 12px;
}
.insight strong { color: #4A6B90; font-weight: 600; }

/* в”Ђв”Ђ Sim Result Cards в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
.sim-card {
    background: #0C1220;
    border: 1px solid rgba(255,255,255,0.055);
    border-left: 2px solid var(--accent-color, #2563EB);
    border-radius: 0 12px 12px 0;
    padding: 18px 18px 14px 18px;
}
.sim-card:hover {
    border-color: rgba(255,255,255,0.10);
    border-left-color: var(--accent-color);
}
.sim-label {
    font-size: 0.67rem;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    color: #2D3E55;
    font-weight: 600;
    margin-bottom: 8px;
}
.sim-value {
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: var(--accent-color, #60A5FA);
    line-height: 1;
    margin-bottom: 8px;
}
.sim-sub {
    font-size: 0.72rem;
    color: #263347;
    border-top: 1px solid rgba(255,255,255,0.04);
    padding-top: 8px;
    margin-top: 2px;
}
.sim-sub strong { color: #2D4A6A; }

/* в”Ђв”Ђ Slider overrides в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
div[data-testid="stSlider"] p {
    font-size: 0.78rem !important;
    color: #3D5470 !important;
    font-family: 'Inter', sans-serif !important;
}
.stSlider [data-baseweb="slider"] { padding-bottom: 0; }

/* в”Ђв”Ђ Radio overrides в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
div[data-testid="stRadio"] p,
div[data-testid="stRadio"] label {
    font-size: 0.78rem !important;
    color: #3D5470 !important;
}

/* в”Ђв”Ђ Streamlit caption в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
.stCaption p { color: #263347 !important; font-size: 0.72rem !important; }
</style>
""", unsafe_allow_html=True)

# в”Ђв”Ђ SVG icons в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
ICONS = {
    "ticket":   '<svg fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>',
    "churn":    '<svg fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"/></svg>',
    "margin":   '<svg fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    "toxic":    '<svg fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
    "grid":     '<svg fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M3 14h18M10 3v18M14 3v18"/></svg>',
    "bar":      '<svg fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>',
    "channel":  '<svg fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>',
    "sim":      '<svg fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>',
    "lightning":'<svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>',
    "save":     '<svg fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"/></svg>',
    "shield":   '<svg fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>',
    "trend":    '<svg fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>',
}

def ico(key: str, color: str = "#4A6080") -> str:
    return f'<span style="color:{color}; display:flex; align-items:center;">{ICONS.get(key,"")}</span>'


def section(icon_key: str, title: str, desc: str = "", accent: str = "#2563EB") -> None:
    desc_html = f'<div class="sec-desc">{desc}</div>' if desc else ""
    st.markdown(f"""
        <div class="sec">
            <div class="sec-icon" style="border-color:rgba(255,255,255,0.07);">{ico(icon_key, accent)}</div>
            <div class="sec-text">
                <div class="sec-title">{title}</div>
                {desc_html}
            </div>
            <div class="sec-line"></div>
        </div>
    """, unsafe_allow_html=True)


# в”Ђв”Ђ Plotly shared theme в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
PLOT_LAYOUT = dict(
    paper_bgcolor="#070B14",
    plot_bgcolor="#070B14",
    font=dict(family="Inter", color="#2D4060", size=11),
    margin=dict(l=0, r=0, t=22, b=0),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.01,
        xanchor="right", x=1, bgcolor="rgba(0,0,0,0)",
        font=dict(size=10, color="#3D5470"),
    ),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#263347", size=10)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False, tickfont=dict(color="#263347", size=10)),
)


@st.cache_resource
def load_db():
    return get_connection()


def render() -> None:
    """Embed-safe entry point. Called by hub.py. No set_page_config."""
    # в”Ђв”Ђ Open page wrapper в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    try:
        con = load_db()
    except Exception as e:
        st.error(f"РџРѕРјРёР»РєР° РїС–РґРєР»СЋС‡РµРЅРЅСЏ РґРѕ DuckDB: {e}")
        st.info("Р—Р°РїСѓСЃС‚С–С‚СЊ `python generate_support_data.py` РґР»СЏ РіРµРЅРµСЂР°С†С–С— РґР°РЅРёС….")
        st.stop()

    # в”Ђв”Ђ Top navigation bar в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    st.markdown(f"""
        <div class="top-nav">
            <div class="nav-logo">
                <div class="nav-logo-mark">{ico("lightning","#FFFFFF")}</div>
                <div>
                    <div class="nav-title">EverHelp вЂ” РђРЅР°Р»С–С‚РёРєР° РћРїРµСЂР°С†С–Р№ РџС–РґС‚СЂРёРјРєРё</div>
                    <div class="nav-sub">Zendesk Tickets в†’ DuckDB In-Memory OLAP в†’ P&amp;L Р’РїР»РёРІ</div>
                </div>
            </div>
            <div class="nav-right">
                <div class="pill"><div class="pulse"></div> LIVE OLAP</div>
                <div class="pill-neutral">300+ FTE</div>
                <div class="pill-neutral">C-Level Audit</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # в”Ђв”Ђ KPI Strip в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    kpis = get_executive_kpis(con)
    breached = kpis["m2_churn_breached_pct"]
    clean    = kpis["m2_churn_clean_pct"]
    delta    = kpis["m2_churn_penalty_delta"]

    c1, c2, c3, c4 = st.columns(4, gap="small")

    with c1:
        st.markdown(f"""
            <div class="kpi" style="--glow:rgba(37,99,235,0.06);">
                <div class="kpi-accent-bar" style="--accent-color:#2563EB;"></div>
                <div class="kpi-top">
                    <div class="kpi-tag">Р’Р°СЂС‚С–СЃС‚СЊ С‚С–РєРµС‚Сѓ</div>
                    <div class="kpi-badge" style="background:rgba(37,99,235,0.10);color:#60A5FA;">РћРїРµСЂР°С†С–Р№РЅР°</div>
                </div>
                <div class="kpi-num" style="color:#F1F5F9;">${kpis['blended_cost_per_ticket']:.2f}</div>
                <div class="kpi-foot">
                    РЎСѓРєСѓРїРЅС– РІРёС‚СЂР°С‚Рё: <strong>${kpis['total_support_cost']:,.0f}</strong>
                    &nbsp;В·&nbsp; {kpis['total_tickets']:,} С‚С–РєРµС‚С–РІ
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="kpi" style="--glow:rgba(225,29,72,0.06);">
                <div class="kpi-accent-bar" style="--accent-color:#E11D48;"></div>
                <div class="kpi-top">
                    <div class="kpi-tag">РЁС‚СЂР°С„ РІС–РґС‚РѕРєСѓ (M2)</div>
                    <div class="kpi-badge" style="background:rgba(225,29,72,0.10);color:#FB7185;">FRT &gt; 25С…РІ</div>
                </div>
                <div class="kpi-num" style="color:#FB7185;">+{delta:.1f}%</div>
                <div class="kpi-foot">
                    Р— РїРѕСЂСѓС€РµРЅРЅСЏРј: <strong style="color:#F43F5E;">{breached:.1f}%</strong>
                    &nbsp;vs&nbsp; Р‘РµР· РїРѕСЂСѓС€РµРЅСЊ: {clean:.1f}%
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="kpi" style="--glow:rgba(5,150,105,0.06);">
                <div class="kpi-accent-bar" style="--accent-color:#059669;"></div>
                <div class="kpi-top">
                    <div class="kpi-tag">Р§РёСЃС‚Р° РјР°СЂР¶Р° РїС–РґС‚СЂРёРјРєРё</div>
                    <div class="kpi-badge" style="background:rgba(5,150,105,0.10);color:#34D399;">P&amp;L</div>
                </div>
                <div class="kpi-num" style="color:#10B981;">{kpis['net_support_margin_pct']:.1f}%</div>
                <div class="kpi-foot">
                    Р§РёСЃС‚РёР№ P&amp;L: <strong>${kpis['total_net_pnl']:,.0f}</strong>
                    &nbsp;В·&nbsp; Р’РёСЂСѓС‡РєР°: ${kpis['total_revenue']:,.0f}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
            <div class="kpi" style="--glow:rgba(220,38,38,0.06);">
                <div class="kpi-accent-bar" style="--accent-color:#DC2626;"></div>
                <div class="kpi-top">
                    <div class="kpi-tag">РўРѕРєСЃРёС‡РЅС– Р°РєР°СѓРЅС‚Рё</div>
                    <div class="kpi-badge" style="background:rgba(220,38,38,0.10);color:#F87171;">Р—Р±РёС‚РєРѕРІС–</div>
                </div>
                <div class="kpi-num" style="color:#F87171;">{kpis['toxic_accounts_count']}</div>
                <div class="kpi-foot">
                    РџСЂСЏРјРёР№ Р·Р±РёС‚РѕРє: <strong style="color:#EF4444;">${kpis['toxic_loss_usd']:,.0f}</strong>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # в”Ђв”Ђ Cohort Retention Heatmap в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    section("grid", "РљРѕРіРѕСЂС‚РЅР° РјР°С‚СЂРёС†СЏ СѓС‚СЂРёРјР°РЅРЅСЏ РєР»С–С”РЅС‚С–РІ",
            "РЈС‚СЂРёРјР°РЅРЅСЏ РїС–РґРїРёСЃРѕРє % РІС–Рґ РњС–СЃСЏС†СЏ 0 РґРѕ РњС–СЃСЏС†СЏ 11 В· СЂРѕР·РїРѕРґС–Р» Р·Р° СЏРєС–СЃС‚СЋ SLA РѕРЅР±РѕСЂРґРёРЅРіСѓ",
            "#2563EB")

    filt_col, _ = st.columns([3, 5])
    with filt_col:
        sla_toggle = st.radio(
            "Р¤С–Р»СЊС‚СЂ СЃРµРіРјРµРЅС‚Сѓ:",
            options=["РЈСЃС– РєРѕРіРѕСЂС‚Рё", "РџРѕСЂСѓС€РµРЅРЅСЏ SLA (>25С…РІ)", "РЇРєС–СЃРЅРёР№ РѕРЅР±РѕСЂРґРёРЅРі (в‰¤25С…РІ)"],
            horizontal=True,
        )

    filter_map = {
        "РЈСЃС– РєРѕРіРѕСЂС‚Рё":               "All",
        "РџРѕСЂСѓС€РµРЅРЅСЏ SLA (>25С…РІ)":     "SLA Breached (>25m)",
        "РЇРєС–СЃРЅРёР№ РѕРЅР±РѕСЂРґРёРЅРі (в‰¤25С…РІ)": "Clean Onboarding (<=25m)",
    }
    df_m = get_cohort_retention_matrix(con, filter_mode=filter_map[sla_toggle])

    month_cols = [f"M{m:02d}" for m in range(12)]
    z_vals     = df_m[month_cols].values
    cohorts    = df_m["cohort_month"].tolist()
    annots     = [["" if pd.isna(v) else f"{v:.0f}%" for v in row] for row in z_vals]

    colorscale = [
        [0.0,  "#0C1525"],
        [0.25, "#0F2347"],
        [0.50, "#1D3A7A"],
        [0.70, "#1D5FB8"],
        [0.85, "#2B8CE0"],
        [1.0,  "#10B981"],
    ]

    fig_hm = go.Figure(go.Heatmap(
        z=z_vals, x=[f"РњС–СЃСЏС†СЊ {m}" for m in range(12)], y=cohorts,
        text=annots, texttemplate="%{text}",
        textfont={"size": 11, "color": "rgba(255,255,255,0.85)", "family": "Inter"},
        colorscale=colorscale, zmin=30, zmax=100,
        colorbar=dict(
            title=dict(text="РЈС‚СЂРёРјР°РЅРЅСЏ %", font=dict(color="#263347", size=10, family="Inter")),
            tickfont=dict(color="#263347", size=10, family="Inter"),
            thickness=10, len=0.92, outlinewidth=0,
        ),
        hoverongaps=False,
        hovertemplate="<b>%{y}</b><br>%{x}: <b>%{z:.1f}%</b><extra></extra>",
    ))
    layout = {**PLOT_LAYOUT, "height": 360}
    layout["yaxis"] = dict(gridcolor="rgba(255,255,255,0.03)", autorange="reversed",
                           tickfont=dict(color="#3D5470", size=10.5, family="Inter"), zeroline=False)
    layout["xaxis"] = dict(showgrid=False, zeroline=False,
                           tickfont=dict(color="#263347", size=10, family="Inter"))
    fig_hm.update_layout(**layout)
    st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # в”Ђв”Ђ Unit Economics + Channel в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    cu1, cu2 = st.columns(2, gap="medium")

    with cu1:
        section("bar", "Р®РЅС–С‚-РµРєРѕРЅРѕРјС–РєР° Р·Р° С‚Р°СЂРёС„РЅРёРј РїР»Р°РЅРѕРј",
                "РЎРµСЂРµРґРЅС–Р№ LTV РєР»С–С”РЅС‚Р° vs РІРёС‚СЂР°С‚Рё РЅР° РїС–РґС‚СЂРёРјРєСѓ ($)", "#2563EB")
        df_t = get_tier_pnl_breakdown(con)

        fig_t = go.Figure()
        fig_t.add_trace(go.Bar(
            name="РЎРµСЂРµРґРЅС–Р№ LTV ($)",
            x=df_t["plan_tier"], y=df_t["avg_ltv_per_user"],
            marker=dict(color="#1D4ED8", opacity=0.9, cornerradius=4),
        ))
        fig_t.add_trace(go.Bar(
            name="Р’РёС‚СЂР°С‚Рё РїС–РґС‚СЂРёРјРєРё ($)",
            x=df_t["plan_tier"], y=df_t["avg_support_cost_per_user"],
            marker=dict(color="#E11D48", opacity=0.8, cornerradius=4),
        ))
        lyt = {**PLOT_LAYOUT, "height": 260, "barmode": "group", "bargap": 0.28}
        lyt["yaxis"] = dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False,
                            tickfont=dict(color="#263347", size=10))
        fig_t.update_layout(**lyt)
        st.plotly_chart(fig_t, use_container_width=True)
        st.markdown("""
            <div class="insight" style="--accent-color:#E11D48;">
                <strong>Basic-С‚Р°СЂРёС„ ($19)</strong>: РІРёСЃРѕРєР° С‡Р°СЃС‚РѕС‚Р° С‚С–РєРµС‚С–РІ С‡РµСЂРµР· Email С„РѕСЂРјСѓС”
                РїСЂСЏРјСѓ РЅРµРіР°С‚РёРІРЅСѓ РјР°СЂР¶Сѓ вЂ” РґР¶РµСЂРµР»Рѕ С‚РѕРєСЃРёС‡РЅРёС… Р°РєР°СѓРЅС‚С–РІ.
            </div>
        """, unsafe_allow_html=True)

    with cu2:
        section("channel", "РџСЂРѕС„С–Р»СЊ РєР°РЅР°Р»С–РІ РїС–РґС‚СЂРёРјРєРё",
                "Р’Р°СЂС‚С–СЃС‚СЊ С‚С–РєРµС‚Сѓ С‚Р° СЂС–РІРµРЅСЊ РїРѕСЂСѓС€РµРЅСЊ SLA РїРѕ РєР°РЅР°Р»Р°С… Р·РІ'СЏР·РєСѓ", "#7C3AED")
        df_ch = get_channel_metrics(con)

        fig_ch = go.Figure()
        fig_ch.add_trace(go.Bar(
            x=df_ch["channel"], y=df_ch["cost_per_ticket"],
            name="Р’Р°СЂС‚С–СЃС‚СЊ С‚С–РєРµС‚Сѓ ($)",
            marker=dict(color="#5B21B6", opacity=0.9, cornerradius=4),
            text=df_ch["cost_per_ticket"].apply(lambda v: f"${v:.2f}"),
            textposition="auto",
            textfont=dict(color="rgba(255,255,255,0.7)", size=11, family="Inter"),
        ))
        fig_ch.add_trace(go.Scatter(
            x=df_ch["channel"], y=df_ch["sla_breach_pct"],
            name="РџРѕСЂСѓС€РµРЅРЅСЏ SLA (%)", yaxis="y2",
            mode="lines+markers",
            marker=dict(size=8, color="#E11D48", line=dict(width=2, color="#070B14")),
            line=dict(width=2.5, color="#E11D48"),
        ))
        lyt2 = {**PLOT_LAYOUT, "height": 260, "bargap": 0.32}
        lyt2["yaxis"]  = dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False,
                               tickfont=dict(color="#263347", size=10))
        lyt2["yaxis2"] = dict(overlaying="y", side="right", showgrid=False, zeroline=False,
                               tickfont=dict(color="#263347", size=10),
                               title=dict(text="SLA Breach %", font=dict(color="#263347", size=10)))
        fig_ch.update_layout(**lyt2)
        st.plotly_chart(fig_ch, use_container_width=True)
        st.markdown("""
            <div class="insight" style="--accent-color:#7C3AED;">
                <strong>Email</strong> вЂ” РЅР°Р№РґРѕСЂРѕР¶С‡РёР№ РєР°РЅР°Р» ($14.00) Р· РЅР°Р№РІРёС‰РёРј СЂС–РІРЅРµРј РїРѕСЂСѓС€РµРЅСЊ SLA.
                РџРµСЂРµРІРµРґРµРЅРЅСЏ С‚СЂР°С„С–РєСѓ РЅР° Chat + AI-РґРµС„Р»РµРєС†С–СЏ РґР°С” РїСЂСЏРјСѓ OPEX-РµРєРѕРЅРѕРјС–СЋ.
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # в”Ђв”Ђ Sensitivity Simulator в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    section("sim", "РЎРёРјСѓР»СЏС‚РѕСЂ С‡СѓС‚Р»РёРІРѕСЃС‚С– P&L",
            "Р’РїР»РёРІ AI-РґРµС„Р»РµРєС†С–С— С‚Р° СЃРєРѕСЂРѕС‡РµРЅРЅСЏ FRT РЅР° С‡РёСЃС‚РёР№ РїСЂРёР±СѓС‚РѕРє вЂ” СЂРµР°Р»СЊРЅРёР№ С‡Р°СЃ",
            "#059669")

    ctrl, res = st.columns([1, 2], gap="large")

    with ctrl:
        st.markdown("""
            <div style="font-size:.68rem; text-transform:uppercase; letter-spacing:.12em;
                        color:#1E3347; font-weight:700; margin-bottom:16px;">
                РћРїРµСЂР°С†С–Р№РЅС– РІР°Р¶РµР»С–
            </div>
        """, unsafe_allow_html=True)
        frt_pct = st.slider(
            "РЎРєРѕСЂРѕС‡РµРЅРЅСЏ С‡Р°СЃСѓ РїРµСЂС€РѕС— РІС–РґРїРѕРІС–РґС– (FRT), %",
            min_value=0, max_value=60, value=25, step=5,
            help="Р—РјРµРЅС€СѓС” РїРѕСЂСѓС€РµРЅРЅСЏ SLA РїС–Рґ С‡Р°СЃ РѕРЅР±РѕСЂРґРёРЅРіСѓ С‚Р° С€С‚СЂР°С„ РІС–РґС‚РѕРєСѓ Сѓ 2-Р№ РјС–СЃСЏС†СЊ.",
        )
        defl_pct = st.slider(
            "AI-РґРµС„Р»РµРєС†С–СЏ С‚Р° СЃР°РјРѕРѕР±СЃР»СѓРіРѕРІСѓРІР°РЅРЅСЏ, %",
            min_value=0, max_value=50, value=20, step=5,
            help="РђРІС‚РѕРјР°С‚РёР·СѓС” С‚РёРїРѕРІС– Email/Chat С‚С–РєРµС‚Рё Р±РµР· РІРёС‚СЂР°С‚ РЅР° FTE-СЂРµСЃСѓСЂСЃ.",
        )

    sim = simulate_margin_sensitivity(con, frt_reduction_pct=frt_pct, ai_deflection_pct=defl_pct)

    with res:
        sr1, sr2, sr3 = st.columns(3, gap="small")
        with sr1:
            st.markdown(f"""
                <div class="sim-card" style="--accent-color:#2563EB;">
                    <div class="sim-label">Р•РєРѕРЅРѕРјС–СЏ РѕРїРµСЂР°С†С–Р№РЅРёС… РІРёС‚СЂР°С‚</div>
                    <div class="sim-value" style="color:#60A5FA;">${sim['deflected_cost_savings']:,.0f}</div>
                    <div class="sim-sub">Р’РёРІС–Р»СЊРЅРµРЅРѕ FTE-СЂРµСЃСѓСЂСЃС–РІ Р·Р° СЂР°С…СѓРЅРѕРє Р°РІС‚РѕРјР°С‚РёР·Р°С†С–С—</div>
                </div>
            """, unsafe_allow_html=True)
        with sr2:
            st.markdown(f"""
                <div class="sim-card" style="--accent-color:#059669;">
                    <div class="sim-label">Р—Р°С…РёС‰РµРЅРёР№ ARR РїС–РґРїРёСЃРѕРє</div>
                    <div class="sim-value" style="color:#10B981;">${sim['revenue_preserved']:,.0f}</div>
                    <div class="sim-sub"><strong>~{sim['saved_m2_accounts']} Р°РєР°СѓРЅС‚С–РІ</strong> СѓС‚СЂРёРјР°РЅРѕ РІС–Рґ РІС–РґС‚РѕРєСѓ</div>
                </div>
            """, unsafe_allow_html=True)
        with sr3:
            st.markdown(f"""
                <div class="sim-card" style="--accent-color:#7C3AED;">
                    <div class="sim-label">РџСЂРёСЂС–СЃС‚ С‡РёСЃС‚РѕРіРѕ P&amp;L Р·Р° СЂС–Рє</div>
                    <div class="sim-value" style="color:#A78BFA;">+${sim['annual_pnl_lift']:,.0f}</div>
                    <div class="sim-sub">
                        РњР°СЂР¶Р°: <strong>{sim['simulated_margin_pct']:.1f}%</strong>
                        &nbsp;(+{sim['margin_delta_pp']:.1f}% Рї.Рї.)
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="insight" style="--accent-color:#059669; margin-top:14px;">
                <strong>Р’РёСЃРЅРѕРІРѕРє РґР»СЏ Head of Ops:</strong> РџРѕС”РґРЅР°РЅРЅСЏ
                <strong>{defl_pct}% AI-РґРµС„Р»РµРєС†С–С—</strong> Tier-1 С‚С–РєРµС‚С–РІ С–Р·
                <strong>СЃРєРѕСЂРѕС‡РµРЅРЅСЏРј FRT РЅР° {frt_pct}%</strong> РїС–Рґ С‡Р°СЃ РѕРЅР±РѕСЂРґРёРЅРіСѓ
                С„РѕСЂРјСѓС” <strong>+${sim['annual_pnl_lift']:,.0f} СЂС–С‡РЅРѕРіРѕ P&amp;L</strong>
                Р±РµР· СЂРѕР·С€РёСЂРµРЅРЅСЏ С€С‚Р°С‚Сѓ 300+ FTE.
            </div>
        """, unsafe_allow_html=True)

    # в”Ђв”Ђ Close page wrapper в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Standalone entry point for direct `streamlit run app.py` launch."""
    st.set_page_config(
        page_title="EverHelp вЂ” Support Ops P&L",
        page_icon="вљЎ",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    render()


if __name__ == "__main__":
    main()

