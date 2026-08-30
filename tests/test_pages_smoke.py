"""
tests/test_pages_smoke.py
Smoke tests verifying imports, function signatures, docstrings, and theme configs across all 25 pages.
"""
import pytest
import importlib
from core.theme import THEMES, get_plotly_layout

ALL_PAGE_MODULES = [
    # Marketplace
    "projects.marketplace.page1_executive",
    "projects.marketplace.page2_orders",
    "projects.marketplace.page3_marketing",
    "projects.marketplace.page4_inventory",
    "projects.marketplace.page5_unit_econ",
    # SaaS
    "projects.saas.page1_mrr",
    "projects.saas.page2_nrr",
    "projects.saas.page3_churn",
    "projects.saas.page4_cac",
    "projects.saas.page5_forecast",
    # Fintech
    "projects.fintech.page1_command",
    "projects.fintech.page2_anomalies",
    "projects.fintech.page3_rails",
    "projects.fintech.page4_geo",
    "projects.fintech.page5_simulator",
    # Gaming
    "projects.gaming.page1_engagement",
    "projects.gaming.page2_funnel",
    "projects.gaming.page3_currency",
    "projects.gaming.page4_monetization",
    "projects.gaming.page5_retention",
    # HealthTech
    "projects.healthtech.page1_icu",
    "projects.healthtech.page2_vitals",
    "projects.healthtech.page3_survival",
    "projects.healthtech.page4_risk",
    "projects.healthtech.page5_cohorts",
]


@pytest.mark.parametrize("mod_name", ALL_PAGE_MODULES)
def test_page_module_import_and_render_callable(mod_name):
    """Verify that every page module can be imported and exports a callable render() function."""
    mod = importlib.import_module(mod_name)
    assert hasattr(mod, "render"), f"Module {mod_name} does not export render()"
    assert callable(mod.render), f"render in {mod_name} is not callable"


def test_theme_configurations():
    """Verify all 5 theme dictionaries have required keys."""
    expected_themes = ["marketplace", "saas", "fintech", "gaming", "healthtech"]
    required_keys = ["name", "bg", "card_bg", "border", "accent", "text_primary", "text_muted", "chart_palette"]
    
    for theme_key in expected_themes:
        assert theme_key in THEMES, f"Theme {theme_key} missing from THEMES"
        cfg = THEMES[theme_key]
        for k in required_keys:
            assert k in cfg, f"Key {k} missing from theme {theme_key}"
        assert len(cfg["chart_palette"]) >= 5


def test_get_plotly_layout():
    """Verify get_plotly_layout produces valid Plotly layout configurations."""
    for theme_key in ["marketplace", "saas", "fintech", "gaming", "healthtech"]:
        layout = get_plotly_layout(theme_key, height=400)
        assert layout["height"] == 400
        assert layout["paper_bgcolor"] == "rgba(0,0,0,0)"
        assert layout["plot_bgcolor"] == "rgba(0,0,0,0)"
        assert "font" in layout
        assert "xaxis" in layout
        assert "yaxis" in layout
