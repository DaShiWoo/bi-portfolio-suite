"""
tests/test_theme.py
Unit tests for core/theme.py: design tokens, WCAG luminance ratios, and HTML component rendering.
"""
import pytest
from core.theme import (
    THEMES,
    get_plotly_layout,
    render_metric_delta,
)


def hex_to_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def rel_luminance(rgb):
    def channel(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(h1: str, h2: str) -> float:
    l1 = rel_luminance(hex_to_rgb(h1))
    l2 = rel_luminance(hex_to_rgb(h2))
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def test_theme_wcag_contrast():
    """Verify that all themes meet WCAG AA contrast standards (>= 4.5:1 for normal text)."""
    for theme_key, cfg in THEMES.items():
        bg = cfg["bg"]
        pri = cfg["text_primary"]
        mut = cfg["text_muted"]
        
        cr_primary = contrast_ratio(pri, bg)
        cr_muted = contrast_ratio(mut, bg)
        
        assert cr_primary >= 4.5, f"Theme {theme_key} primary text fails WCAG AA: {cr_primary:.2f}:1"
        assert cr_muted >= 4.5, f"Theme {theme_key} muted text fails WCAG AA: {cr_muted:.2f}:1"


def test_render_metric_delta_positive():
    html = render_metric_delta(current=120.0, previous=100.0, label="Revenue")
    assert "+20.0%" in html
    assert "#10b981" in html  # emerald green for positive


def test_render_metric_delta_negative():
    html = render_metric_delta(current=80.0, previous=100.0, label="Orders")
    assert "-20.0%" in html
    assert "#ef4444" in html  # red for negative


def test_plotly_layout_colorway():
    for theme_key, cfg in THEMES.items():
        layout = get_plotly_layout(theme_key)
        assert layout["colorway"] == cfg["chart_palette"]
        assert len(layout["colorway"]) >= 5
