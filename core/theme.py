"""
core/theme.py
Design System, Component Library, and Theme Engine for BI Portfolio Hub.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

THEMES = {
    "marketplace": {
        "name": "Marketplace & E-Commerce",
        "bg": "#09090b",
        "card_bg": "rgba(24, 24, 27, 0.65)",
        "border": "rgba(255, 255, 255, 0.08)",
        "accent": "#f59e0b",
        "accent_secondary": "#10b981",
        "text_primary": "#fafafa",
        "text_muted": "#a1a1aa",
        "chart_palette": ["#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6"],
        "glow": "0 0 25px rgba(245, 158, 11, 0.15)"
    },
    "saas": {
        "name": "B2B SaaS & Subscriptions",
        "bg": "#0b0d17",
        "card_bg": "rgba(20, 24, 45, 0.6)",
        "border": "rgba(139, 92, 246, 0.2)",
        "accent": "#8b5cf6",
        "accent_secondary": "#6366f1",
        "text_primary": "#f8fafc",
        "text_muted": "#94a3b8",
        "chart_palette": ["#8b5cf6", "#6366f1", "#38bdf8", "#ec4899", "#10b981"],
        "glow": "0 0 25px rgba(139, 92, 246, 0.2)"
    },
    "fintech": {
        "name": "Fintech & Anti-Fraud Engine",
        "bg": "#05080f",
        "card_bg": "rgba(10, 19, 32, 0.7)",
        "border": "rgba(16, 185, 129, 0.2)",
        "accent": "#10b981",
        "accent_secondary": "#f59e0b",
        "text_primary": "#ecfdf5",
        "text_muted": "#6ee7b7",
        "chart_palette": ["#10b981", "#f59e0b", "#ef4444", "#3b82f6", "#06b6d4"],
        "glow": "0 0 25px rgba(16, 185, 129, 0.2)"
    },
    "gaming": {
        "name": "Game LiveOps & Virtual Economy",
        "bg": "#070919",
        "card_bg": "rgba(16, 21, 51, 0.65)",
        "border": "rgba(6, 182, 212, 0.25)",
        "accent": "#06b6d4",
        "accent_secondary": "#ec4899",
        "text_primary": "#f0fdfa",
        "text_muted": "#a5f3fc",
        "chart_palette": ["#06b6d4", "#ec4899", "#a855f7", "#eab308", "#10b981"],
        "glow": "0 0 30px rgba(6, 182, 212, 0.25)"
    },
    "healthtech": {
        "name": "HealthTech & Clinical Telemetry",
        "bg": "#071317",
        "card_bg": "rgba(13, 31, 38, 0.65)",
        "border": "rgba(20, 184, 166, 0.2)",
        "accent": "#14b8a6",
        "accent_secondary": "#38bdf8",
        "text_primary": "#f0fdf4",
        "text_muted": "#99f6e4",
        "chart_palette": ["#14b8a6", "#38bdf8", "#34d399", "#818cf8", "#f43f5e"],
        "glow": "0 0 25px rgba(20, 184, 166, 0.2)"
    }
}

def apply_theme(theme_key: str):
    """Inject dynamic CSS tailored to the selected theme."""
    cfg = THEMES.get(theme_key, THEMES["marketplace"])
    
    custom_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    .stApp {{
        background-color: {cfg['bg']};
        color: {cfg['text_primary']};
    }}
    
    header[data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: {cfg['bg']};
        border-right: 1px solid {cfg['border']};
    }}
    
    /* Glassmorphic Card */
    .bi-card {{
        background: {cfg['card_bg']};
        border: 1px solid {cfg['border']};
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: {cfg['glow']}, 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .bi-card:hover {{
        border-color: {cfg['accent']};
        transform: translateY(-2px);
    }}
    
    .kpi-title {{
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {cfg['text_muted']};
        font-weight: 600;
        margin-bottom: 4px;
    }}
    .kpi-value {{
        font-size: 1.85rem;
        font-weight: 800;
        color: {cfg['text_primary']};
        letter-spacing: -0.02em;
        margin-bottom: 4px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .kpi-delta-pos {{
        color: #10b981;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.14);
        padding: 2px 8px;
        border-radius: 9999px;
    }}
    .kpi-delta-neg {{
        color: #ef4444;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        background: rgba(239, 68, 68, 0.14);
        padding: 2px 8px;
        border-radius: 9999px;
    }}
    .kpi-subtext {{
        font-size: 0.75rem;
        color: {cfg['text_muted']};
        margin-top: 5px;
    }}
    
    /* Section Headers */
    .bi-section-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 20px;
        margin-bottom: 12px;
        padding-bottom: 6px;
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
    
    /* What-If Box */
    .what-if-container {{
        background: rgba(255, 255, 255, 0.02);
        border: 1px dashed {cfg['accent']};
        border-radius: 12px;
        padding: 16px;
        margin-top: 14px;
        margin-bottom: 18px;
    }}
    
    /* Buttons */
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

def render_kpi(title: str, value: str, delta: str = None, is_positive: bool = True, subtext: str = None, badge: str = None):
    badge_html = f'<span style="float: right; font-size: 0.7rem; opacity: 0.8;">{badge}</span>' if badge else ''
    delta_html = ''
    if delta:
        delta_class = "kpi-delta-pos" if is_positive else "kpi-delta-neg"
        arrow = "▲" if is_positive else "▼"
        delta_html = f'<div style="margin-top: 4px;"><span class="{delta_class}">{arrow} {delta}</span></div>'
    subtext_html = f'<div class="kpi-subtext">{subtext}</div>' if subtext else ''
    
    card_html = f"""
    <div class="bi-card">
        <div class="kpi-title">{title} {badge_html}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
        {subtext_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_section_header(title: str, badge: str = None, subtitle: str = None):
    badge_html = f'<span class="bi-section-badge">{badge}</span>' if badge else ''
    sub_html = f'<div style="font-size: 0.82rem; color: #a1a1aa; margin-top: -6px; margin-bottom: 10px;">{subtitle}</div>' if subtitle else ''
    html = f"""
    <div class="bi-section-header">
        <div class="bi-section-title">{title}</div>
        {badge_html}
    </div>
    {sub_html}
    """
    st.markdown(html, unsafe_allow_html=True)

def render_export_button(df: pd.DataFrame, filename: str, label: str = "📥 Export Slice to CSV"):
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=label,
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        key=f"dl_{filename}"
    )

def get_plotly_layout(theme_key: str, height: int = 350) -> dict:
    cfg = THEMES.get(theme_key, THEMES["marketplace"])
    return dict(
        height=height,
        margin=dict(l=20, r=20, t=35, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans, sans-serif", color=cfg['text_muted'], size=11),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.06)',
            linecolor='rgba(255,255,255,0.1)',
            tickfont=dict(color=cfg['text_muted'])
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.06)',
            linecolor='rgba(255,255,255,0.1)',
            tickfont=dict(color=cfg['text_muted'])
        ),
        colorway=cfg['chart_palette'],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=cfg['text_primary'])
        )
    )
