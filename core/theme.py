"""
core/theme.py
Design System, Component Library, and Theme Engine for BI Portfolio Hub.
Upgraded with animated gradient backgrounds, shimmer KPI cards, glassmorphism
tabs, sidebar navigation pills, accent scrollbar, filter banners, and metric
delta helpers.
"""
import base64
import functools
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------------------------------------------------------
# Theme registry
# ---------------------------------------------------------------------------

THEMES = {
    "marketplace": {
        "name": "Marketplace & E-Commerce",
        "bg": "#09090b",
        "gradient": (
            "radial-gradient(ellipse 90% 70% at 20% 10%, rgba(245,158,11,0.18) 0%, transparent 60%),"
            "radial-gradient(ellipse 60% 80% at 80% 90%, rgba(16,185,129,0.10) 0%, transparent 55%),"
            "radial-gradient(ellipse 100% 100% at 50% 50%, #09090b 40%, #0c0a03 100%)"
        ),
        "card_bg": "rgba(24, 24, 27, 0.65)",
        "border": "rgba(255, 255, 255, 0.08)",
        "accent": "#f59e0b",
        "accent_secondary": "#10b981",
        "text_primary": "#fafafa",
        "text_muted": "#a1a1aa",
        "chart_palette": ["#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6"],
        "glow": "0 0 25px rgba(245, 158, 11, 0.15)",
        "tab_glow": "0 0 14px rgba(245,158,11,0.55)",
    },
    "saas": {
        "name": "B2B SaaS & Subscriptions",
        "bg": "#0b0d17",
        "gradient": (
            "radial-gradient(ellipse 80% 60% at 10% 5%, rgba(99,102,241,0.22) 0%, transparent 55%),"
            "radial-gradient(ellipse 70% 90% at 90% 95%, rgba(139,92,246,0.16) 0%, transparent 60%),"
            "radial-gradient(ellipse 100% 100% at 50% 50%, #0b0d17 30%, #06071a 100%)"
        ),
        "card_bg": "rgba(20, 24, 45, 0.6)",
        "border": "rgba(139, 92, 246, 0.2)",
        "accent": "#8b5cf6",
        "accent_secondary": "#6366f1",
        "text_primary": "#f8fafc",
        "text_muted": "#94a3b8",
        "chart_palette": ["#8b5cf6", "#6366f1", "#38bdf8", "#ec4899", "#10b981"],
        "glow": "0 0 25px rgba(139, 92, 246, 0.2)",
        "tab_glow": "0 0 14px rgba(139,92,246,0.6)",
    },
    "fintech": {
        "name": "Fintech & Anti-Fraud Engine",
        "bg": "#05080f",
        "gradient": (
            "radial-gradient(ellipse 100% 60% at 15% 15%, rgba(16,185,129,0.15) 0%, transparent 55%),"
            "radial-gradient(ellipse 60% 80% at 85% 80%, rgba(245,158,11,0.10) 0%, transparent 55%),"
            "repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(16,185,129,0.03) 40px),"
            "repeating-linear-gradient(90deg, transparent, transparent 39px, rgba(16,185,129,0.03) 40px),"
            "radial-gradient(ellipse 100% 100% at 50% 50%, #05080f 30%, #020809 100%)"
        ),
        "card_bg": "rgba(10, 19, 32, 0.7)",
        "border": "rgba(16, 185, 129, 0.2)",
        "accent": "#10b981",
        "accent_secondary": "#f59e0b",
        "text_primary": "#ecfdf5",
        "text_muted": "#6ee7b7",
        "chart_palette": ["#10b981", "#f59e0b", "#ef4444", "#3b82f6", "#06b6d4"],
        "glow": "0 0 25px rgba(16, 185, 129, 0.2)",
        "tab_glow": "0 0 14px rgba(16,185,129,0.6)",
    },
    "gaming": {
        "name": "Game LiveOps & Virtual Economy",
        "bg": "#070919",
        "gradient": (
            "radial-gradient(ellipse 80% 55% at 15% 10%, rgba(6,182,212,0.18) 0%, transparent 55%),"
            "radial-gradient(ellipse 70% 70% at 85% 85%, rgba(236,72,153,0.18) 0%, transparent 55%),"
            "repeating-linear-gradient(0deg, transparent, transparent 29px, rgba(6,182,212,0.04) 30px),"
            "repeating-linear-gradient(90deg, transparent, transparent 29px, rgba(236,72,153,0.04) 30px),"
            "radial-gradient(ellipse 100% 100% at 50% 50%, #070919 25%, #03040f 100%)"
        ),
        "card_bg": "rgba(16, 21, 51, 0.65)",
        "border": "rgba(6, 182, 212, 0.25)",
        "accent": "#06b6d4",
        "accent_secondary": "#ec4899",
        "text_primary": "#f0fdfa",
        "text_muted": "#a5f3fc",
        "chart_palette": ["#06b6d4", "#ec4899", "#a855f7", "#eab308", "#10b981"],
        "glow": "0 0 30px rgba(6, 182, 212, 0.25)",
        "tab_glow": "0 0 14px rgba(6,182,212,0.65)",
    },
    "healthtech": {
        "name": "HealthTech & Clinical Telemetry",
        "bg": "#071317",
        "gradient": (
            "radial-gradient(ellipse 90% 60% at 20% 10%, rgba(20,184,166,0.16) 0%, transparent 55%),"
            "radial-gradient(ellipse 70% 80% at 80% 90%, rgba(56,189,248,0.12) 0%, transparent 55%),"
            "radial-gradient(ellipse 100% 100% at 50% 50%, #071317 35%, #030c10 100%)"
        ),
        "card_bg": "rgba(13, 31, 38, 0.65)",
        "border": "rgba(20, 184, 166, 0.2)",
        "accent": "#14b8a6",
        "accent_secondary": "#38bdf8",
        "text_primary": "#f0fdf4",
        "text_muted": "#99f6e4",
        "chart_palette": ["#14b8a6", "#38bdf8", "#34d399", "#818cf8", "#f43f5e"],
        "glow": "0 0 25px rgba(20, 184, 166, 0.2)",
        "tab_glow": "0 0 14px rgba(20,184,166,0.6)",
    },
}


# ---------------------------------------------------------------------------
# apply_theme — injects all CSS
# ---------------------------------------------------------------------------

def apply_theme(theme_key: str):
    """Inject dynamic CSS tailored to the selected theme."""
    cfg = THEMES.get(theme_key, THEMES["marketplace"])

    custom_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* Animated gradient background with solid fallback */
    .stApp {{
        background-color: {cfg['bg']};
        background-image: {cfg['gradient']};
        background-attachment: fixed;
        color: {cfg['text_primary']};
    }}

    @media (prefers-reduced-motion: reduce) {{
        .bi-card::after {{
            animation: none !important;
        }}
        .bi-card:hover {{
            transform: none !important;
            animation: none !important;
        }}
    }}

    /* Shimmer keyframes for KPI cards */
    @keyframes shimmer {{
        0%   {{ background-position: -400px 0; }}
        100% {{ background-position:  400px 0; }}
    }}
    @keyframes pulse-border {{
        0%, 100% {{ box-shadow: {cfg['glow']}, 0 8px 32px rgba(0,0,0,0.4); }}
        50%       {{ box-shadow: 0 0 35px {cfg['accent']}40, 0 8px 32px rgba(0,0,0,0.4); }}
    }}

    /* Header */
    header[data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
    }}

    /* Sidebar — navigation pill style */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {cfg['bg']} 0%, {cfg['bg']} 100%);
        border-right: 1px solid {cfg['border']};
    }}
    section[data-testid="stSidebar"] label {{
        display: block;
        padding: 7px 14px;
        border-radius: 9px;
        margin-bottom: 3px;
        font-size: 0.85rem;
        font-weight: 500;
        color: {cfg['text_muted']};
        transition: all 0.18s ease;
        cursor: pointer;
    }}
    section[data-testid="stSidebar"] label:hover {{
        background: rgba(255,255,255,0.06);
        color: {cfg['text_primary']};
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: {cfg['border']};
        margin: 10px 0;
    }}

    /* Glassmorphic Card */
    .bi-card {{
        background: {cfg['card_bg']};
        border: 1px solid {cfg['border']};
        border-left: 3px solid {cfg['accent']};
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: {cfg['glow']}, 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    .bi-card::after {{
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 60%; height: 100%;
        background: linear-gradient(
            120deg,
            transparent 0%,
            rgba(255,255,255,0.04) 50%,
            transparent 100%
        );
        background-size: 400px 100%;
        animation: shimmer 3.5s infinite linear;
        pointer-events: none;
    }}
    .bi-card:hover {{
        border-color: {cfg['accent']};
        border-left-color: {cfg['accent']};
        transform: translateY(-3px);
        animation: pulse-border 2s ease-in-out infinite;
    }}

    /* KPI typography */
    .kpi-title {{
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: {cfg['text_muted']};
        font-weight: 600;
        margin-bottom: 5px;
    }}
    .kpi-value {{
        font-size: 2.4rem;
        font-weight: 800;
        color: {cfg['text_primary']};
        letter-spacing: -0.025em;
        line-height: 1.1;
        margin-bottom: 5px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .kpi-delta-pos {{
        color: #10b981;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.14);
        padding: 2px 9px;
        border-radius: 9999px;
    }}
    .kpi-delta-neg {{
        color: #ef4444;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        background: rgba(239, 68, 68, 0.14);
        padding: 2px 9px;
        border-radius: 9999px;
    }}
    .kpi-subtext {{
        font-size: 0.73rem;
        color: {cfg['text_muted']};
        margin-top: 5px;
    }}

    /* KPI progress bar */
    .kpi-progress-track {{
        width: 100%;
        height: 4px;
        background: rgba(255,255,255,0.07);
        border-radius: 9999px;
        margin-top: 10px;
        overflow: hidden;
    }}
    .kpi-progress-fill {{
        height: 100%;
        border-radius: 9999px;
        background: linear-gradient(90deg, {cfg['accent']}, {cfg['accent_secondary']});
        transition: width 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
    }}

    /* Section Headers */
    .bi-section-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 20px;
        margin-bottom: 12px;
        padding-bottom: 7px;
        border-bottom: 1px solid {cfg['border']};
    }}
    .bi-section-title {{
        font-size: 1.2rem;
        font-weight: 700;
        color: {cfg['text_primary']};
        letter-spacing: -0.01em;
    }}
    .bi-section-badge {{
        font-size: 0.7rem;
        font-weight: 600;
        background: {cfg['accent']};
        color: #000;
        padding: 2px 8px;
        border-radius: 6px;
        text-transform: uppercase;
    }}

    /* Filter banner */
    .filter-banner {{
        background: linear-gradient(90deg, {cfg['accent']}18, {cfg['accent']}06);
        border: 1px solid {cfg['accent']}44;
        border-left: 3px solid {cfg['accent']};
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 0.8rem;
        font-weight: 600;
        color: {cfg['accent']};
        letter-spacing: 0.04em;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .filter-banner .filter-count {{
        color: {cfg['text_primary']};
        font-weight: 700;
    }}

    /* Glassmorphism Tabs */
    [data-baseweb="tab-list"] {{
        background: {cfg['card_bg']};
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid {cfg['border']};
        gap: 2px;
    }}
    [data-baseweb="tab"] {{
        border-radius: 9px !important;
        padding: 6px 18px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: {cfg['text_muted']} !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }}
    [data-baseweb="tab"]:hover {{
        color: {cfg['text_primary']} !important;
        background: rgba(255,255,255,0.05) !important;
    }}
    [aria-selected="true"][data-baseweb="tab"] {{
        background: {cfg['accent']}22 !important;
        color: {cfg['accent']} !important;
        box-shadow: {cfg['tab_glow']} !important;
        border: 1px solid {cfg['accent']}44 !important;
    }}

    /* What-If Box */
    .what-if-container {{
        background: rgba(255, 255, 255, 0.02);
        border: 1px dashed {cfg['accent']};
        border-radius: 12px;
        padding: 16px;
        margin-top: 14px;
        margin-bottom: 18px;
    }}

    /* Filter expander (dark glass panel) */
    [data-testid="stExpander"] {{
        background: {cfg['card_bg']} !important;
        border: 1px solid {cfg['border']} !important;
        border-radius: 12px !important;
        backdrop-filter: blur(12px) !important;
        margin-top: 14px !important;
        margin-bottom: 14px !important;
    }}
    [data-testid="stSidebar"] [data-testid="stExpander"] {{
        margin-top: 16px !important;
        margin-bottom: 12px !important;
    }}
    [data-testid="stExpander"] summary {{
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        color: {cfg['text_muted']} !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        padding: 10px 14px !important;
    }}
    [data-testid="stExpander"] summary:hover {{
        color: {cfg['accent']} !important;
    }}
    [data-testid="stExpander"][open] summary {{
        border-bottom: 1px solid {cfg['border']};
        color: {cfg['accent']} !important;
    }}

    /* Executive Profile Badge Styles */
    .executive-profile-link {{
        text-decoration: none !important;
        color: inherit !important;
        display: inline-block;
        flex-shrink: 0;
    }}
    .executive-profile-card {{
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(18, 24, 38, 0.72);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.11);
        border-radius: 12px;
        padding: 8px 14px 8px 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        cursor: pointer;
        user-select: none;
    }}
    .executive-profile-card:hover {{
        border-color: rgba(99, 102, 241, 0.5) !important;
        background: rgba(24, 32, 54, 0.88) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(37, 99, 235, 0.28) !important;
    }}
    .profile-avatar-container {{
        position: relative;
        width: 44px;
        height: 44px;
        flex-shrink: 0;
    }}
    .profile-avatar-img {{
        width: 44px;
        height: 44px;
        border-radius: 50%;
        object-fit: cover;
        border: 1.5px solid rgba(255, 255, 255, 0.22);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        display: block;
    }}
    .profile-avatar-fallback {{
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: #fff;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
    }}
    .profile-status-dot {{
        position: absolute;
        bottom: 0px;
        right: 0px;
        width: 11px;
        height: 11px;
        background: #10b981;
        border: 2px solid #0b0e17;
        border-radius: 50%;
        box-shadow: 0 0 6px rgba(16, 185, 129, 0.9);
    }}
    .profile-text-col {{
        display: flex;
        flex-direction: column;
        gap: 2px;
    }}
    .profile-name-row {{
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .profile-name {{
        font-size: 0.86rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }}
    .profile-linkedin-icon {{
        display: flex;
        align-items: center;
    }}
    .profile-outlink-arrow {{
        font-size: 0.75rem;
        color: #94a3b8;
        transition: transform 0.2s ease, color 0.2s ease;
    }}
    .executive-profile-card:hover .profile-outlink-arrow {{
        color: #60a5fa;
        transform: translate(1px, -1px);
    }}
    .profile-title {{
        font-size: 0.70rem;
        font-weight: 500;
        color: #94a3b8;
        line-height: 1.2;
    }}
    .profile-availability-pill {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.67rem;
        font-weight: 600;
        color: #34d399;
        background: rgba(16, 185, 129, 0.10);
        border: 1px solid rgba(16, 185, 129, 0.24);
        border-radius: 5px;
        padding: 1px 6px;
        margin-top: 2px;
        width: fit-content;
        white-space: nowrap;
    }}
    .profile-beacon {{
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: #10b981;
        animation: profile-beacon-pulse 2s infinite;
    }}
    @keyframes profile-beacon-pulse {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 4px rgba(16, 185, 129, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    /* Custom accent scrollbar */
    ::-webkit-scrollbar {{
        width: 5px;
        height: 5px;
    }}
    ::-webkit-scrollbar-track {{
        background: transparent;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {cfg['accent']}66;
        border-radius: 9999px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {cfg['accent']}cc;
    }}

    /* Download Button */
    .stDownloadButton > button {{
        background-color: {cfg['card_bg']};
        color: {cfg['text_primary']};
        border: 1px solid {cfg['border']};
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }}
    .stDownloadButton > button:hover {{
        border-color: {cfg['accent']};
        background-color: {cfg['accent']};
        color: #000;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# render_kpi — glassmorphic KPI card with left-border, shimmer, progress bar
# ---------------------------------------------------------------------------

def render_kpi(
    title: str,
    value: str,
    delta: str = None,
    is_positive: bool = True,
    subtext: str = None,
    badge: str = None,
    progress: float = None,
):
    """
    Render a glassmorphic KPI card.

    Parameters
    ----------
    title       : card label
    value       : formatted value string
    delta       : change label (e.g. '+12.4%')
    is_positive : controls green/red colouring of delta
    subtext     : small footnote beneath delta
    badge       : optional emoji/text badge shown top-right
    progress    : optional float 0-1 to render a progress bar
    """
    badge_html = (
        f'<span style="float:right;font-size:0.72rem;opacity:0.75;margin-top:2px;">{badge}</span>'
        if badge else ""
    )
    delta_html = ""
    if delta:
        delta_class = "kpi-delta-pos" if is_positive else "kpi-delta-neg"
        arrow = "\u25b2" if is_positive else "\u25bc"
        delta_html = (
            f'<div style="margin-top:5px;">'
            f'<span class="{delta_class}">{arrow} {delta}</span>'
            f'</div>'
        )
    subtext_html = (
        f'<div class="kpi-subtext">{subtext}</div>' if subtext else ""
    )
    progress_html = ""
    if progress is not None:
        pct = max(0.0, min(1.0, float(progress))) * 100
        progress_html = (
            f'<div class="kpi-progress-track">'
            f'<div class="kpi-progress-fill" style="width:{pct:.1f}%;"></div>'
            f'</div>'
        )

    parts = [
        '<div class="bi-card">',
        f'<div class="kpi-title">{title} {badge_html}</div>',
        f'<div class="kpi-value">{value}</div>',
    ]
    if delta_html:
        parts.append(delta_html)
    if subtext_html:
        parts.append(subtext_html)
    if progress_html:
        parts.append(progress_html)
    parts.append('</div>')

    card_html = "".join(parts)
    st.markdown(card_html, unsafe_allow_html=True)



# ---------------------------------------------------------------------------
# render_section_header
# ---------------------------------------------------------------------------

def render_section_header(title: str, badge: str = None, subtitle: str = None):
    """Render a themed section divider with optional badge and subtitle."""
    badge_html = (
        f'<span class="bi-section-badge">{badge}</span>' if badge else ""
    )
    sub_html = (
        f'<div style="font-size:0.82rem;color:#a1a1aa;margin-top:-6px;margin-bottom:10px;">'
        f'{subtitle}</div>'
        if subtitle else ""
    )
    html = f"""
    <div class="bi-section-header">
        <div class="bi-section-title">{title}</div>
        {badge_html}
    </div>
    {sub_html}
    """
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# render_filter_row — active-filter status banner
# ---------------------------------------------------------------------------

def render_filter_row(label: str, count_filtered: int, count_total: int):
    """
    Render a styled HTML banner showing how many records pass current filters.

    Example output:
        v REVENUE FILTERS ACTIVE - showing 4,821 of 15,000 records
    """
    pct = (count_filtered / count_total * 100) if count_total else 0
    html = f"""
    <div class="filter-banner">
        <span>\u25bc {label.upper()} FILTERS ACTIVE</span>
        <span style="opacity:0.4;">\u2014</span>
        <span>showing
            <span class="filter-count">{count_filtered:,}</span>
            of
            <span class="filter-count">{count_total:,}</span>
            records
            <span style="opacity:0.55;font-weight:500;">({pct:.1f}%)</span>
        </span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# render_metric_delta — formatted HTML metric with real computed delta
# ---------------------------------------------------------------------------

def render_metric_delta(
    current: float,
    previous: float,
    label: str,
    format_str: str = ",.0f",
    prefix: str = "$",
) -> str:
    """
    Compute real delta % between current and previous values and return
    a styled HTML snippet suitable for st.markdown.

    Parameters
    ----------
    current    : current period value
    previous   : prior period value (used as baseline for % change)
    label      : metric label text
    format_str : Python format spec for the numeric value (e.g. ',.0f', '.2%')
    prefix     : currency / unit prefix (e.g. '$', 'E', '')

    Returns
    -------
    str : HTML string - call st.markdown(render_metric_delta(...), unsafe_allow_html=True)
    """
    if previous and previous != 0:
        delta_pct = (current - previous) / abs(previous) * 100
    else:
        delta_pct = 0.0

    is_pos = delta_pct >= 0
    delta_color = "#10b981" if is_pos else "#ef4444"
    delta_bg = "rgba(16,185,129,0.13)" if is_pos else "rgba(239,68,68,0.13)"
    arrow = "\u25b2" if is_pos else "\u25bc"
    sign = "+" if is_pos else ""

    formatted_value = f"{prefix}{current:{format_str}}"
    formatted_delta = f"{sign}{delta_pct:.1f}%"

    html = f"""
    <div style="margin-bottom:6px;">
        <div style="font-size:0.78rem;text-transform:uppercase;letter-spacing:0.08em;
                    color:#a1a1aa;font-weight:600;margin-bottom:3px;">{label}</div>
        <div style="font-size:2rem;font-weight:800;letter-spacing:-0.02em;
                    line-height:1.1;margin-bottom:4px;">{formatted_value}</div>
        <span style="font-size:0.78rem;font-weight:600;color:{delta_color};
                     background:{delta_bg};padding:2px 9px;border-radius:9999px;
                     display:inline-flex;align-items:center;gap:4px;">
            {arrow} {formatted_delta} vs prior period
        </span>
    </div>
    """
    return html


# ---------------------------------------------------------------------------
# render_export_button
# ---------------------------------------------------------------------------

def render_export_button(df: pd.DataFrame, filename: str, label: str = "\U0001f4e5 Export Slice to CSV"):
    """Download button for a filtered DataFrame slice."""
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        key=f"dl_{filename}",
    )


# ---------------------------------------------------------------------------
# get_plotly_layout — shared chart layout factory
# ---------------------------------------------------------------------------

def get_plotly_layout(theme_key: str, height: int = 350) -> dict:
    """
    Return a Plotly layout dict pre-configured for the active theme.
    Grid lines are very subtle; axis lines are invisible.
    """
    cfg = THEMES.get(theme_key, THEMES["marketplace"])
    return dict(
        height=height,
        margin=dict(l=20, r=20, t=35, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Plus Jakarta Sans, sans-serif",
            color=cfg["text_muted"],
            size=11,
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(0,0,0,0)",
            zerolinecolor="rgba(255,255,255,0.04)",
            tickfont=dict(color=cfg["text_muted"]),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(0,0,0,0)",
            zerolinecolor="rgba(255,255,255,0.04)",
            tickfont=dict(color=cfg["text_muted"]),
        ),
        colorway=cfg["chart_palette"],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=cfg["text_primary"]),
        ),
    )


# ---------------------------------------------------------------------------
# Executive Profile Badge & Header Component
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def get_avatar_base64() -> str:
    """Return base64 data URI of user avatar, prioritizing optimized assets."""
    candidates = [
        Path("assets/profile_avatar_opt.png"),
        Path("assets/profile_avatar.png"),
        Path("docs/linkedin_avatar_pro.jpg"),
        Path("docs/linkedin_avatar_exact.jpg"),
    ]
    for p in candidates:
        if p.exists():
            mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:{mime};base64,{b64}"
    return ""


def get_profile_badge_html() -> str:
    """
    Generate the Executive Profile Badge HTML with avatar, online status beacon,
    C-Level positioning, and direct LinkedIn clickable link.
    """
    avatar_uri = get_avatar_base64()
    if avatar_uri:
        avatar_markup = f'<img src="{avatar_uri}" alt="Danylo" class="profile-avatar-img" />'
    else:
        avatar_markup = '<div class="profile-avatar-fallback">DW</div>'

    return f"""<a href="https://www.linkedin.com/in/dashiwoo/" target="_blank" rel="noopener noreferrer" class="executive-profile-link" title="Open Danylo's LinkedIn Profile (in/dashiwoo)">
        <div class="executive-profile-card">
            <div class="profile-avatar-container">
                {avatar_markup}
                <span class="profile-status-dot" title="Available for projects"></span>
            </div>
            <div class="profile-text-col">
                <div class="profile-name-row">
                    <span class="profile-name">Danylo (DaShiWoo)</span>
                    <span class="profile-linkedin-icon" title="Verified LinkedIn">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="#0A66C2">
                            <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.2V10.9H6.46M7.83 6.2a1.66 1.66 0 0 0-1.67 1.67c0 .92.75 1.67 1.67 1.67a1.67 1.67 0 0 0 1.67-1.67c0-.92-.75-1.67-1.67-1.67Z"/>
                        </svg>
                    </span>
                    <span class="profile-outlink-arrow">&#8599;</span>
                </div>
                <div class="profile-title">Principal BI &amp; Data Architect</div>
                <div class="profile-availability-pill">
                    <span class="profile-beacon"></span>
                    <span>Available for Consulting / Q3-Q4 Contracts</span>
                </div>
            </div>
        </div>
    </a>"""


def render_page_header(title: str, subtitle: str, theme_key: str = "marketplace") -> None:
    """
    Render a responsive top-level dashboard header banner with the Executive Profile
    Badge positioned in the top-right corner opposite the H1 title.
    """
    cfg = THEMES.get(theme_key, THEMES["marketplace"])
    title_color = cfg.get("text_primary", "#ffffff")
    sub_color = cfg.get("text_muted", "#94a3b8")
    badge_html = get_profile_badge_html()

    header_html = f"""
    <div class="hub-header-wrap" style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        margin-bottom: 18px;
        padding-bottom: 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.07);
        flex-wrap: wrap;
    ">
        <div style="flex: 1 1 460px; min-width: 280px;">
            <h1 style="font-size: 1.95rem; font-weight: 800; margin-bottom: 4px; color: {title_color}; letter-spacing: -0.02em;">
                {title}
            </h1>
            <p style="color: {sub_color}; font-size: 0.88rem; margin-top: 0; margin-bottom: 0; line-height: 1.45;">
                {subtitle}
            </p>
        </div>
        <div style="flex-shrink: 0;">
            {badge_html}
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

