"""
cases/support_ops_pnl/db_engine.py
In-Memory DuckDB Analytical Engine for Support Ops P&L.

Executes direct SQL queries against Parquet files without intermediate Pandas transformations:
- Support Cost to LTV Ratio & Toxic Accounts Identification
- Cohort Retention Matrices with SLA exposure toggles
- AI Deflection & FRT Reduction Sensitivity Simulation
"""

import os
from typing import Any, Dict, Optional
import duckdb
import pandas as pd

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(MODULE_DIR, "data")
COHORTS_PARQUET = os.path.join(DATA_DIR, "subscriptions_cohorts.parquet").replace("\\", "/")
TICKETS_PARQUET = os.path.join(DATA_DIR, "zendesk_tickets.parquet").replace("\\", "/")


def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Initializes an in-memory DuckDB connection and creates analytical views
    directly over the Parquet datasets.
    """
    con = duckdb.connect(database=":memory:")
    
    if not os.path.exists(COHORTS_PARQUET) or not os.path.exists(TICKETS_PARQUET):
        raise FileNotFoundError(
            f"Parquet files missing in {DATA_DIR}. Run generate_support_data.py first."
        )

    # 1. Base views over Parquet
    con.execute(f"CREATE OR REPLACE VIEW zendesk_tickets AS SELECT * FROM read_parquet('{TICKETS_PARQUET}');")
    con.execute(f"CREATE OR REPLACE VIEW subscriptions_cohorts AS SELECT * FROM read_parquet('{COHORTS_PARQUET}');")

    # 2. Pre-aggregated user-level tickets view
    con.execute("""
        CREATE OR REPLACE VIEW v_user_ticket_summary AS
        SELECT
            user_id,
            COUNT(ticket_id) AS total_tickets,
            SUM(resolution_cost_usd) AS total_support_cost,
            AVG(first_reply_time_min) AS avg_frt_min,
            AVG(satisfaction_score) AS avg_csat,
            COUNT(CASE WHEN first_reply_time_min > 25.0 THEN 1 END) AS breached_tickets_count,
            COUNT(CASE WHEN channel = 'Email' THEN 1 END) AS email_tickets,
            COUNT(CASE WHEN channel = 'Chat' THEN 1 END) AS chat_tickets,
            COUNT(CASE WHEN channel = 'WhatsApp' THEN 1 END) AS whatsapp_tickets
        FROM zendesk_tickets
        GROUP BY user_id;
    """)

    # 3. User-level Unit Economics (LTV vs Support Cost)
    con.execute("""
        CREATE OR REPLACE VIEW v_user_financials AS
        SELECT
            c.user_id,
            c.signup_date,
            c.cohort_month,
            c.plan_tier,
            c.monthly_revenue,
            c.status,
            c.tenure_months,
            c.early_sla_breach,
            (c.monthly_revenue * c.tenure_months) AS total_ltv,
            COALESCE(s.total_tickets, 0) AS total_tickets,
            COALESCE(s.total_support_cost, 0.0) AS total_support_cost,
            COALESCE(s.avg_frt_min, 0.0) AS avg_frt_min,
            COALESCE(s.avg_csat, 0.0) AS avg_csat,
            ((c.monthly_revenue * c.tenure_months) - COALESCE(s.total_support_cost, 0.0)) AS net_margin_usd,
            CASE 
                WHEN (c.monthly_revenue * c.tenure_months) > 0 
                THEN (COALESCE(s.total_support_cost, 0.0) / (c.monthly_revenue * c.tenure_months)) * 100.0
                ELSE 0.0 
            END AS support_cost_to_ltv_pct,
            CASE 
                WHEN COALESCE(s.total_support_cost, 0.0) > (c.monthly_revenue * c.tenure_months) 
                THEN 1 
                ELSE 0 
            END AS is_toxic_account
        FROM subscriptions_cohorts c
        LEFT JOIN v_user_ticket_summary s ON c.user_id = s.user_id;
    """)

    return con


def get_executive_kpis(con: duckdb.DuckDBPyConnection) -> Dict[str, Any]:
    """Calculates top-line executive KPIs for C-Level Ops review."""
    query = """
        SELECT
            (SELECT COUNT(*) FROM zendesk_tickets) AS total_tickets,
            (SELECT SUM(resolution_cost_usd) FROM zendesk_tickets) AS total_support_cost,
            (SELECT AVG(resolution_cost_usd) FROM zendesk_tickets) AS blended_cost_per_ticket,
            (SELECT AVG(first_reply_time_min) FROM zendesk_tickets) AS avg_frt_min,
            (SELECT COUNT(CASE WHEN first_reply_time_min > 25.0 THEN 1 END) * 100.0 / COUNT(*) FROM zendesk_tickets) AS sla_breach_rate_pct,
            (SELECT SUM(total_ltv) FROM v_user_financials) AS total_revenue,
            (SELECT SUM(net_margin_usd) FROM v_user_financials) AS total_net_pnl,
            (SELECT COUNT(*) FROM v_user_financials WHERE is_toxic_account = 1) AS toxic_accounts_count,
            (SELECT SUM(total_support_cost - total_ltv) FROM v_user_financials WHERE is_toxic_account = 1) AS toxic_loss_usd,
            -- Month 2 Churn Comparison
            (SELECT COUNT(CASE WHEN tenure_months <= 2 THEN 1 END) * 100.0 / COUNT(*) 
             FROM subscriptions_cohorts WHERE early_sla_breach = true) AS m2_churn_breached_pct,
            (SELECT COUNT(CASE WHEN tenure_months <= 2 THEN 1 END) * 100.0 / COUNT(*) 
             FROM subscriptions_cohorts WHERE early_sla_breach = false) AS m2_churn_clean_pct
    """
    row = con.execute(query).df().iloc[0]
    
    total_rev = float(row["total_revenue"])
    total_cost = float(row["total_support_cost"])
    net_margin_pct = ((total_rev - total_cost) / total_rev) * 100.0 if total_rev > 0 else 0.0
    churn_breached = float(row["m2_churn_breached_pct"])
    churn_clean = float(row["m2_churn_clean_pct"])

    return {
        "total_tickets": int(row["total_tickets"]),
        "total_support_cost": total_cost,
        "blended_cost_per_ticket": float(row["blended_cost_per_ticket"]),
        "avg_frt_min": float(row["avg_frt_min"]),
        "sla_breach_rate_pct": float(row["sla_breach_rate_pct"]),
        "total_revenue": total_rev,
        "total_net_pnl": float(row["total_net_pnl"]),
        "net_support_margin_pct": net_margin_pct,
        "toxic_accounts_count": int(row["toxic_accounts_count"]),
        "toxic_loss_usd": float(row["toxic_loss_usd"]),
        "m2_churn_breached_pct": churn_breached,
        "m2_churn_clean_pct": churn_clean,
        "m2_churn_penalty_delta": churn_breached - churn_clean
    }


def get_cohort_retention_matrix(con: duckdb.DuckDBPyConnection, filter_mode: str = "All") -> pd.DataFrame:
    """
    Computes triangular cohort retention matrix with support SLA exposure filter.
    filter_mode: 'All', 'SLA Breached (>25m)', 'Clean Onboarding (<=25m)'
    """
    where_clause = "1=1"
    if filter_mode == "SLA Breached (>25m)":
        where_clause = "early_sla_breach = true"
    elif filter_mode == "Clean Onboarding (<=25m)":
        where_clause = "early_sla_breach = false"

    query = f"""
        WITH filtered AS (
            SELECT cohort_month, tenure_months
            FROM subscriptions_cohorts
            WHERE {where_clause}
        ),
        cohort_counts AS (
            SELECT cohort_month, COUNT(*) AS base_users
            FROM filtered
            GROUP BY cohort_month
        )
        SELECT 
            c.cohort_month,
            t.base_users,
            100.0 AS "M00",
            ROUND(COUNT(CASE WHEN c.tenure_months >= 1 THEN 1 END) * 100.0 / t.base_users, 1) AS "M01",
            ROUND(COUNT(CASE WHEN c.tenure_months >= 2 THEN 1 END) * 100.0 / t.base_users, 1) AS "M02",
            ROUND(COUNT(CASE WHEN c.tenure_months >= 3 THEN 1 END) * 100.0 / t.base_users, 1) AS "M03",
            ROUND(COUNT(CASE WHEN c.tenure_months >= 4 THEN 1 END) * 100.0 / t.base_users, 1) AS "M04",
            ROUND(COUNT(CASE WHEN c.tenure_months >= 5 THEN 1 END) * 100.0 / t.base_users, 1) AS "M05",
            ROUND(COUNT(CASE WHEN c.tenure_months >= 6 THEN 1 END) * 100.0 / t.base_users, 1) AS "M06",
            ROUND(COUNT(CASE WHEN c.tenure_months >= 7 THEN 1 END) * 100.0 / t.base_users, 1) AS "M07",
            ROUND(COUNT(CASE WHEN c.tenure_months >= 8 THEN 1 END) * 100.0 / t.base_users, 1) AS "M08",
            ROUND(COUNT(CASE WHEN c.tenure_months >= 9 THEN 1 END) * 100.0 / t.base_users, 1) AS "M09",
            ROUND(COUNT(CASE WHEN c.tenure_months >= 10 THEN 1 END) * 100.0 / t.base_users, 1) AS "M10",
            ROUND(COUNT(CASE WHEN c.tenure_months >= 11 THEN 1 END) * 100.0 / t.base_users, 1) AS "M11"
        FROM filtered c
        JOIN cohort_counts t ON c.cohort_month = t.cohort_month
        GROUP BY c.cohort_month, t.base_users
        ORDER BY c.cohort_month;
    """
    df = con.execute(query).df()
    
    # Enforce triangular matrix: mask out future months based on cohort age
    # Base dataset runs 2025-09 (idx 0) to 2026-08 (idx 11)
    cohort_order = sorted(df["cohort_month"].unique().tolist())
    total_cohorts = len(cohort_order)
    
    for idx, month_str in enumerate(cohort_order):
        # max observable lifecycle months for this cohort
        max_m = total_cohorts - idx - 1
        for m in range(1, 12):
            col = f"M{m:02d}"
            if m > max_m and col in df.columns:
                df.loc[df["cohort_month"] == month_str, col] = None

    return df


def get_tier_pnl_breakdown(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Calculates Support Cost vs LTV and toxic account distribution across plan tiers."""
    query = """
        SELECT
            plan_tier,
            COUNT(*) AS total_accounts,
            SUM(is_toxic_account) AS toxic_accounts,
            ROUND(SUM(is_toxic_account) * 100.0 / COUNT(*), 1) AS toxic_rate_pct,
            ROUND(SUM(total_ltv), 2) AS total_ltv,
            ROUND(SUM(total_support_cost), 2) AS total_support_cost,
            ROUND(SUM(net_margin_usd), 2) AS net_margin_usd,
            ROUND((SUM(net_margin_usd) / SUM(total_ltv)) * 100.0, 1) AS margin_pct,
            ROUND(AVG(total_support_cost), 2) AS avg_support_cost_per_user,
            ROUND(AVG(total_ltv), 2) AS avg_ltv_per_user
        FROM v_user_financials
        GROUP BY plan_tier
        ORDER BY CASE plan_tier WHEN 'Basic' THEN 1 WHEN 'Pro' THEN 2 ELSE 3 END;
    """
    return con.execute(query).df()


def get_channel_metrics(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Operational channel unit economics and deflection baseline."""
    query = """
        SELECT
            channel,
            COUNT(*) AS ticket_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM zendesk_tickets), 1) AS volume_share_pct,
            ROUND(AVG(first_reply_time_min), 1) AS avg_frt_min,
            ROUND(AVG(full_resolution_time_min), 1) AS avg_resolution_min,
            ROUND(COUNT(CASE WHEN first_reply_time_min > 25.0 THEN 1 END) * 100.0 / COUNT(*), 1) AS sla_breach_pct,
            ROUND(AVG(resolution_cost_usd), 2) AS cost_per_ticket,
            ROUND(SUM(resolution_cost_usd), 2) AS total_cost_usd,
            ROUND(AVG(satisfaction_score), 2) AS avg_csat
        FROM zendesk_tickets
        GROUP BY channel
        ORDER BY total_cost_usd DESC;
    """
    return con.execute(query).df()


def simulate_margin_sensitivity(
    con: duckdb.DuckDBPyConnection,
    frt_reduction_pct: float,
    ai_deflection_pct: float
) -> Dict[str, Any]:
    """
    Dynamic P&L Simulator:
    1. AI Deflection: Diverts a % of Email and Chat tickets, saving full unit resolution cost.
    2. FRT Reduction: Decreases early onboarding SLA breaches, preserving Month-2 retention.
    """
    # 1. Base support costs from Email and Chat
    query_channels = """
        SELECT
            SUM(CASE WHEN channel IN ('Email', 'Chat') THEN resolution_cost_usd ELSE 0 END) AS automatable_cost,
            COUNT(CASE WHEN channel IN ('Email', 'Chat') THEN 1 END) AS automatable_tickets,
            (SELECT COUNT(*) FROM subscriptions_cohorts WHERE early_sla_breach = true) AS breached_accounts,
            (SELECT AVG(monthly_revenue * tenure_months) FROM subscriptions_cohorts WHERE early_sla_breach = true) AS avg_breached_ltv,
            (SELECT (
                (SELECT COUNT(CASE WHEN tenure_months <= 2 THEN 1 END) * 1.0 / COUNT(*) FROM subscriptions_cohorts WHERE early_sla_breach = true) -
                (SELECT COUNT(CASE WHEN tenure_months <= 2 THEN 1 END) * 1.0 / COUNT(*) FROM subscriptions_cohorts WHERE early_sla_breach = false)
            )) AS churn_penalty_rate
        FROM zendesk_tickets
    """
    res = con.execute(query_channels).df().iloc[0]
    automatable_cost = float(res["automatable_cost"])
    breached_accounts = float(res["breached_accounts"])
    avg_breached_ltv = float(res["avg_breached_ltv"])
    churn_penalty_rate = float(res["churn_penalty_rate"])

    # Calculations:
    # 1. Cost avoided via AI Deflection
    deflected_cost_savings = automatable_cost * (ai_deflection_pct / 100.0)
    
    # 2. Subscriptions saved via FRT reduction
    # Each % reduction in FRT prevents a corresponding proportion of early SLA breaches
    prevented_breaches = breached_accounts * (frt_reduction_pct / 100.0)
    saved_m2_accounts = prevented_breaches * max(0.0, churn_penalty_rate)
    revenue_preserved = saved_m2_accounts * avg_breached_ltv * 1.35  # Account for extended lifetime value

    # Baseline P&L
    base_kpis = get_executive_kpis(con)
    base_rev = base_kpis["total_revenue"]
    base_cost = base_kpis["total_support_cost"]
    base_margin_pct = base_kpis["net_support_margin_pct"]

    # Simulated P&L
    sim_rev = base_rev + revenue_preserved
    sim_cost = max(0.0, base_cost - deflected_cost_savings)
    sim_pnl = sim_rev - sim_cost
    sim_margin_pct = ((sim_rev - sim_cost) / sim_rev) * 100.0 if sim_rev > 0 else 0.0

    annual_pnl_lift = (sim_pnl - base_kpis["total_net_pnl"])

    return {
        "ai_deflection_pct": ai_deflection_pct,
        "frt_reduction_pct": frt_reduction_pct,
        "deflected_cost_savings": deflected_cost_savings,
        "saved_m2_accounts": int(round(saved_m2_accounts)),
        "revenue_preserved": revenue_preserved,
        "annual_pnl_lift": annual_pnl_lift,
        "base_margin_pct": base_margin_pct,
        "simulated_margin_pct": sim_margin_pct,
        "margin_delta_pp": sim_margin_pct - base_margin_pct
    }
