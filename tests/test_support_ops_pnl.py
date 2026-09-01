"""
tests/test_support_ops_pnl.py
Automated Verification Suite for cases/support_ops_pnl (DuckDB + Streamlit).
"""

import os
import py_compile
import pytest
import pandas as pd
import duckdb

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases", "support_ops_pnl")


def test_syntax_compilation():
    """Verify all 3 python files compile cleanly without any syntax errors."""
    for script in ["generate_support_data.py", "db_engine.py", "app.py"]:
        script_path = os.path.join(CASE_DIR, script)
        assert os.path.exists(script_path), f"File {script_path} must exist"
        py_compile.compile(script_path, doraise=True)


def test_parquet_data_integrity():
    """Verify that parquet datasets exist and have non-zero row counts."""
    data_dir = os.path.join(CASE_DIR, "data")
    cohorts_path = os.path.join(data_dir, "subscriptions_cohorts.parquet")
    tickets_path = os.path.join(data_dir, "zendesk_tickets.parquet")

    assert os.path.exists(cohorts_path), "subscriptions_cohorts.parquet missing"
    assert os.path.exists(tickets_path), "zendesk_tickets.parquet missing"

    df_c = pd.read_parquet(cohorts_path)
    df_t = pd.read_parquet(tickets_path)

    assert len(df_c) >= 5000, f"Expected >= 5000 cohorts, got {len(df_c)}"
    assert len(df_t) >= 20000, f"Expected >= 20000 tickets, got {len(df_t)}"
    assert "early_sla_breach" in df_c.columns
    assert "first_reply_time_min" in df_t.columns


def test_duckdb_engine_kpis():
    """Verify get_connection and get_executive_kpis calculations."""
    import sys
    if CASE_DIR not in sys.path:
        sys.path.insert(0, CASE_DIR)
    
    from db_engine import get_connection, get_executive_kpis

    con = get_connection()
    kpis = get_executive_kpis(con)

    assert kpis["total_tickets"] > 0
    assert kpis["blended_cost_per_ticket"] > 0
    assert kpis["total_revenue"] > 0
    assert kpis["net_support_margin_pct"] > 50.0  # Healthy gross SaaS margin
    assert kpis["m2_churn_penalty_delta"] > 0  # Proof of correlation


def test_cohort_retention_matrix():
    """Verify triangular cohort retention matrix computation across all filters."""
    import sys
    if CASE_DIR not in sys.path:
        sys.path.insert(0, CASE_DIR)
    
    from db_engine import get_connection, get_cohort_retention_matrix

    con = get_connection()

    for filter_mode in ["All", "SLA Breached (>25m)", "Clean Onboarding (<=25m)"]:
        df_matrix = get_cohort_retention_matrix(con, filter_mode=filter_mode)
        assert len(df_matrix) == 12, f"Expected 12 cohort rows, got {len(df_matrix)}"
        assert "M00" in df_matrix.columns
        assert "M11" in df_matrix.columns
        # M00 is always 100%
        assert (df_matrix["M00"] == 100.0).all()


def test_sensitivity_simulation():
    """Verify P&L sensitivity model dynamics."""
    import sys
    if CASE_DIR not in sys.path:
        sys.path.insert(0, CASE_DIR)
    
    from db_engine import get_connection, simulate_margin_sensitivity

    con = get_connection()

    # Zero lever should yield zero additional lift
    sim_zero = simulate_margin_sensitivity(con, frt_reduction_pct=0, ai_deflection_pct=0)
    assert sim_zero["annual_pnl_lift"] == pytest.approx(0.0, abs=1e-3)

    # 30% FRT reduction + 20% AI Deflection should yield significant dollar lift
    sim_active = simulate_margin_sensitivity(con, frt_reduction_pct=30, ai_deflection_pct=20)
    assert sim_active["annual_pnl_lift"] > 50000.0
    assert sim_active["deflected_cost_savings"] > 0
    assert sim_active["revenue_preserved"] > 0
    assert sim_active["margin_delta_pp"] > 0
