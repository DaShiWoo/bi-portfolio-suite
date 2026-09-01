"""
cases/support_ops_pnl/generate_support_data.py
High-Fidelity Synthetic Data Generator for Support Ops P&L Analytics.

Generates:
1. data/subscriptions_cohorts.parquet:
   - ~6,000 accounts spanning 12 cohort months (2025-09 to 2026-08).
   - Tiers: Basic ($19/mo), Pro ($49/mo), Enterprise ($199/mo).
   - Realistic tenure, cohort retention, and churn dates.
   - Enforces deterministic correlation: early onboarding SLA breach (FRT > 25 min in first 14 days)
     triggers +35% relative churn spike in Month 2.

2. data/zendesk_tickets.parquet:
   - ~45,000 tickets linked by user_id across channels (Chat, Email, WhatsApp).
   - Realistic FRT, Full Resolution Time, CSAT (1-5), channel-differentiated resolution costs,
     and operational tags (bug, billing, onboarding, cancellation).
"""

import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RANDOM_SEED = 42

TIER_CONFIG = {
    "Basic": {"mrr": 19.0, "share": 0.50, "base_m2_retention": 0.76},
    "Pro": {"mrr": 49.0, "share": 0.35, "base_m2_retention": 0.88},
    "Enterprise": {"mrr": 199.0, "share": 0.15, "base_m2_retention": 0.94},
}

CHANNEL_CONFIG = {
    "Chat": {"share": 0.45, "unit_cost": 8.50, "frt_mean": 8.0, "frt_std": 6.0},
    "Email": {"share": 0.35, "unit_cost": 14.00, "frt_mean": 38.0, "frt_std": 22.0},
    "WhatsApp": {"share": 0.20, "unit_cost": 6.20, "frt_mean": 12.0, "frt_std": 8.0},
}


def generate_support_ops_datasets(num_accounts: int = 6000) -> None:
    np.random.seed(RANDOM_SEED)
    os.makedirs(DATA_DIR, exist_ok=True)

    start_date = datetime(2025, 9, 1)
    end_date = datetime(2026, 8, 31)
    total_days = (end_date - start_date).days

    # -------------------------------------------------------------
    # 1. Generate Subscriptions & Cohorts
    # -------------------------------------------------------------
    user_ids = [f"USR-{100000 + i}" for i in range(num_accounts)]
    
    tiers = np.random.choice(
        ["Basic", "Pro", "Enterprise"],
        size=num_accounts,
        p=[TIER_CONFIG["Basic"]["share"], TIER_CONFIG["Pro"]["share"], TIER_CONFIG["Enterprise"]["share"]]
    )

    # Random signup offsets across 365 days
    signup_day_offsets = np.random.randint(0, total_days, size=num_accounts)
    signup_dates = [start_date + timedelta(days=int(d)) for d in signup_day_offsets]
    cohort_months = [d.strftime("%Y-%m") for d in signup_dates]
    mrrs = [TIER_CONFIG[t]["mrr"] for t in tiers]

    # Decide which users experience early support tickets (days 0-14)
    # ~55% of users file a ticket in onboarding
    has_early_ticket = np.random.rand(num_accounts) < 0.55
    # Probability of an early SLA breach (FRT > 25 min)
    early_sla_breached = np.zeros(num_accounts, dtype=bool)
    
    for i in range(num_accounts):
        if has_early_ticket[i]:
            # ~42% chance of early ticket having delayed response > 25 min
            early_sla_breached[i] = np.random.rand() < 0.42

    # Churn decision modeled by tier + early SLA breach
    statuses = []
    churn_dates = []
    lifetimes_months = []

    for i in range(num_accounts):
        tier = tiers[i]
        signup = signup_dates[i]
        breached = early_sla_breached[i]
        
        # Max possible tenure up to end_date
        max_possible_months = max(1, int((end_date - signup).days / 30.4))
        
        base_m2 = TIER_CONFIG[tier]["base_m2_retention"]
        # If breached, relative churn in Month 2 increases by ~35%
        m2_retention = base_m2 * (0.65 if breached else 1.0)
        
        # Determine survival across lifetime months
        survived = True
        actual_tenure_months = max_possible_months
        
        # Month 1 survival is high (~96%)
        if np.random.rand() > 0.96:
            survived = False
            actual_tenure_months = 1
        elif np.random.rand() > m2_retention:
            # Month 2 churn hit!
            survived = False
            actual_tenure_months = 2
        else:
            # Subsequent months retention decay (~3% monthly churn)
            for m in range(3, max_possible_months + 1):
                monthly_churn_prob = 0.04 if breached else 0.025
                if np.random.rand() < monthly_churn_prob:
                    survived = False
                    actual_tenure_months = m
                    break
                    
        lifetimes_months.append(actual_tenure_months)
        
        if not survived:
            churn_offset = int(actual_tenure_months * 30.4) + np.random.randint(-5, 5)
            churn_dt = signup + timedelta(days=max(5, churn_offset))
            if churn_dt > end_date:
                churn_dt = end_date
                statuses.append("active")
                churn_dates.append(None)
            else:
                statuses.append("churned")
                churn_dates.append(churn_dt.strftime("%Y-%m-%d"))
        else:
            statuses.append("active")
            churn_dates.append(None)

    df_cohorts = pd.DataFrame({
        "user_id": user_ids,
        "signup_date": [d.strftime("%Y-%m-%d") for d in signup_dates],
        "cohort_month": cohort_months,
        "plan_tier": tiers,
        "monthly_revenue": mrrs,
        "status": statuses,
        "churn_date": churn_dates,
        "tenure_months": lifetimes_months,
        "early_sla_breach": early_sla_breached
    })

    cohorts_parquet_path = os.path.join(DATA_DIR, "subscriptions_cohorts.parquet")
    table_cohorts = pa.Table.from_pandas(df_cohorts)
    pq.write_table(table_cohorts, cohorts_parquet_path, compression="zstd")
    print(f"[OK] Generated {len(df_cohorts):,} cohort subscriptions -> {cohorts_parquet_path}")

    # -------------------------------------------------------------
    # 2. Generate Zendesk Tickets
    # -------------------------------------------------------------
    ticket_ids = []
    t_user_ids = []
    t_created_ats = []
    t_frt_mins = []
    t_full_res_mins = []
    t_channels = []
    t_agent_ids = []
    t_costs = []
    t_csats = []
    t_tags = []

    ticket_counter = 1
    channels_list = ["Chat", "Email", "WhatsApp"]
    channel_probs = [CHANNEL_CONFIG[c]["share"] for c in channels_list]
    tag_options = ["bug", "billing", "onboarding", "cancellation"]
    tag_probs = [0.30, 0.35, 0.20, 0.15]
    agents = [f"AGT-{101 + a}" for a in range(60)]

    for i in range(num_accounts):
        uid = user_ids[i]
        signup = signup_dates[i]
        status = statuses[i]
        c_date_str = churn_dates[i]
        c_date = datetime.strptime(c_date_str, "%Y-%m-%d") if c_date_str else end_date
        active_days = max(1, (c_date - signup).days)
        breached = early_sla_breached[i]

        # Determine number of tickets filed by user (scaled to support ops 300+ FTE workload)
        base_rate = 2.2 if tiers[i] == "Enterprise" else (1.4 if tiers[i] == "Pro" else 0.9)
        num_tickets = max(1 if has_early_ticket[i] else 0, np.random.poisson(lam=base_rate * max(1.0, active_days / 30.0)))
        if num_tickets == 0 and has_early_ticket[i]:
            num_tickets = 1

        for t_idx in range(num_tickets):
            if t_idx == 0 and has_early_ticket[i]:
                # Onboarding ticket in first 14 days
                offset_days = np.random.randint(0, min(14, active_days))
                ch = np.random.choice(channels_list, p=[0.30, 0.55, 0.15]) if breached else np.random.choice(channels_list, p=[0.50, 0.25, 0.25])
                tag = "onboarding" if np.random.rand() < 0.65 else np.random.choice(tag_options)
                
                if breached:
                    # Guaranteed SLA breach > 25 min
                    frt = float(np.random.uniform(26.0, 115.0))
                else:
                    frt = float(np.clip(np.random.normal(11.0, 5.0), 2.0, 24.0))
            else:
                offset_days = np.random.randint(0, active_days)
                ch = np.random.choice(channels_list, p=channel_probs)
                cfg = CHANNEL_CONFIG[ch]
                frt = float(np.clip(np.random.normal(cfg["frt_mean"], cfg["frt_std"]), 1.5, 240.0))
                tag = np.random.choice(tag_options, p=tag_probs)

            created_at = signup + timedelta(days=int(offset_days), hours=int(np.random.randint(8, 20)), minutes=int(np.random.randint(0, 59)))
            if created_at > end_date:
                continue

            # Resolution time is FRT + additional investigation time
            full_res = frt + float(np.random.exponential(scale=45.0) + 15.0)
            
            # Unit resolution cost
            unit_base = CHANNEL_CONFIG[ch]["unit_cost"]
            res_cost = round(float(unit_base * (1.0 + (full_res / 180.0) * 0.4) + np.random.normal(0, 0.8)), 2)
            res_cost = max(4.0, res_cost)

            # CSAT score (1-5) derived from FRT and resolution
            if frt > 45.0 or full_res > 180.0:
                csat = int(np.random.choice([1, 2, 3], p=[0.55, 0.35, 0.10]))
            elif frt > 25.0:
                csat = int(np.random.choice([2, 3, 4], p=[0.35, 0.45, 0.20]))
            else:
                csat = int(np.random.choice([3, 4, 5], p=[0.10, 0.35, 0.55]))

            ticket_ids.append(f"TICK-{1000000 + ticket_counter}")
            t_user_ids.append(uid)
            t_created_ats.append(created_at.strftime("%Y-%m-%d %H:%M:%S"))
            t_frt_mins.append(round(frt, 1))
            t_full_res_mins.append(round(full_res, 1))
            t_channels.append(ch)
            t_agent_ids.append(np.random.choice(agents))
            t_costs.append(res_cost)
            t_csats.append(csat)
            t_tags.append(tag)

            ticket_counter += 1

    df_tickets = pd.DataFrame({
        "ticket_id": ticket_ids,
        "user_id": t_user_ids,
        "created_at": t_created_ats,
        "first_reply_time_min": t_frt_mins,
        "full_resolution_time_min": t_full_res_mins,
        "channel": t_channels,
        "agent_id": t_agent_ids,
        "resolution_cost_usd": t_costs,
        "satisfaction_score": t_csats,
        "tags": t_tags
    })

    tickets_parquet_path = os.path.join(DATA_DIR, "zendesk_tickets.parquet")
    table_tickets = pa.Table.from_pandas(df_tickets)
    pq.write_table(table_tickets, tickets_parquet_path, compression="zstd")
    print(f"[OK] Generated {len(df_tickets):,} Zendesk tickets -> {tickets_parquet_path}")


if __name__ == "__main__":
    generate_support_ops_datasets()
