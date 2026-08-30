"""
generate_all_data.py
Comprehensive multi-industry synthetic dataset generator for BI Portfolio Suite.
Generates realistic distributions, correlations, and time series across 5 domains.
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
np.random.seed(42)

print(">> [1/5] Generating Marketplace Data...")
n_orders = 15000
dates = [datetime(2024, 1, 1) + timedelta(days=int(d), seconds=int(s)) 
         for d, s in zip(np.random.uniform(0, 365, n_orders), np.random.uniform(0, 86400, n_orders))]
categories = np.random.choice(["Electronics", "Fashion", "Home & Living", "Beauty & Care", "Sports"], n_orders, p=[0.3, 0.25, 0.2, 0.15, 0.1])
base_prices = {"Electronics": 180, "Fashion": 65, "Home & Living": 95, "Beauty & Care": 45, "Sports": 75}
amounts = [max(15.0, round(float(np.random.normal(base_prices[c], base_prices[c]*0.4)), 2)) for c in categories]
statuses = np.random.choice(["Delivered", "Shipped", "Processing", "Cancelled", "Returned"], n_orders, p=[0.72, 0.10, 0.06, 0.07, 0.05])
channels = np.random.choice(["Search Ads", "Social Media", "Direct/Organic", "Email", "Affiliate"], n_orders, p=[0.35, 0.25, 0.20, 0.12, 0.08])
regions = np.random.choice(["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East"], n_orders, p=[0.4, 0.3, 0.18, 0.07, 0.05])
skus = [f"SKU-{np.random.randint(100, 220)}" for _ in range(n_orders)]

df_market = pd.DataFrame({
    "order_id": [f"ORD-{100000+i}" for i in range(n_orders)],
    "timestamp": dates,
    "date": [d.date() for d in dates],
    "sku": skus,
    "category": categories,
    "amount": amounts,
    "status": statuses,
    "channel": channels,
    "region": regions,
    "take_rate": np.random.uniform(0.12, 0.18, n_orders).round(4)
})
df_market["marketplace_fee"] = (df_market["amount"] * df_market["take_rate"]).round(2)
df_market["cogs"] = (df_market["amount"] * np.random.uniform(0.55, 0.70, n_orders)).round(2)
df_market["profit"] = (df_market["marketplace_fee"] - (df_market["amount"] * 0.03)).round(2)
df_market.to_parquet(os.path.join(DATA_DIR, "marketplace_orders.parquet"), index=False)

# Inventory dataset (120 SKUs)
unique_skus = [f"SKU-{i}" for i in range(100, 220)]
sku_cats = np.random.choice(["Electronics", "Fashion", "Home & Living", "Beauty & Care", "Sports"], len(unique_skus))
sku_stock = np.random.randint(5, 500, len(unique_skus))
sku_velocity = np.random.uniform(0.8, 18.0, len(unique_skus)).round(1) # units/day
days_of_inv = (sku_stock / sku_velocity).round(1)
df_inventory = pd.DataFrame({
    "sku": unique_skus,
    "category": sku_cats,
    "stock_units": sku_stock,
    "daily_velocity": sku_velocity,
    "days_of_inventory": days_of_inv,
    "unit_cost": np.random.uniform(15, 120, len(unique_skus)).round(2),
    "abc_class": np.random.choice(["A (Top 80%)", "B (Next 15%)", "C (Tail 5%)"], len(unique_skus), p=[0.2, 0.3, 0.5]),
    "xyz_class": np.random.choice(["X (Stable)", "Y (Variable)", "Z (Erratic)"], len(unique_skus), p=[0.4, 0.35, 0.25]),
    "stockout_risk": ["CRITICAL (< 7d)" if d < 7 else ("LOW (< 14d)" if d < 14 else "OPTIMAL") for d in days_of_inv]
})
df_inventory.to_parquet(os.path.join(DATA_DIR, "marketplace_inventory.parquet"), index=False)


print(">> [2/5] Generating SaaS Subscriptions Data...")
n_cust = 2000
signup = [datetime(2024, 1, 1) + timedelta(days=int(d)) for d in np.random.uniform(0, 365, n_cust)]
tiers = np.random.choice(["Starter", "Professional", "Enterprise"], n_cust, p=[0.5, 0.35, 0.15])
tier_mrr = {"Starter": 99, "Professional": 499, "Enterprise": 2499}
mrr = [tier_mrr[t] + round(np.random.normal(0, tier_mrr[t]*0.08), 2) for t in tiers]
churn_probs = {"Starter": 0.20, "Professional": 0.08, "Enterprise": 0.02}
churned = [np.random.random() < churn_probs[t] for t in tiers]
reasons = ["Pricing / Budget", "Missing Feature", "Switched to Competitor", "Low Usage / Champion Left", "Acquired / Company Shut"]

df_saas = pd.DataFrame({
    "customer_id": [f"CUST-{1000+i}" for i in range(n_cust)],
    "signup_date": signup,
    "date": [d.date() for d in signup],
    "cohort": [d.strftime("%Y-%m") for d in signup],
    "tier": tiers,
    "mrr": mrr,
    "arr": [m * 12 for m in mrr],
    "churned": churned,
    "churn_reason": [np.random.choice(reasons) if c else "Active" for c in churned],
    "expansion_mrr": [round(max(0, np.random.normal(m*0.22, m*0.08)), 2) if not c else 0 for m, c in zip(mrr, churned)],
    "contraction_mrr": [round(max(0, np.random.normal(m*0.08, m*0.04)), 2) if not c and np.random.random() < 0.15 else 0 for m, c in zip(mrr, churned)],
    "channel": np.random.choice(["Inbound Organic", "Paid Search", "Outbound SDR", "Partner Referrals"], n_cust, p=[0.35, 0.30, 0.20, 0.15]),
    "cac": [round(m * np.random.uniform(3.5, 7.5), 2) for m in mrr],
    "nps": np.random.choice([9, 10, 8, 7, 6, 5], n_cust, p=[0.3, 0.25, 0.25, 0.1, 0.06, 0.04])
})
df_saas.to_parquet(os.path.join(DATA_DIR, "saas_subscriptions.parquet"), index=False)


print(">> [3/5] Generating Fintech & Fraud Data...")
n_txns = 15000
txn_dates = [datetime(2024, 1, 1) + timedelta(days=int(d), seconds=int(s))
             for d, s in zip(np.random.uniform(0, 365, n_txns), np.random.uniform(0, 86400, n_txns))]
methods = np.random.choice(["Credit Card", "Wire Transfer", "Web3/Crypto", "Instant ACH", "Digital Wallet"], n_txns, p=[0.45, 0.20, 0.15, 0.12, 0.08])
base_txn = {"Credit Card": 120, "Wire Transfer": 4500, "Web3/Crypto": 850, "Instant ACH": 350, "Digital Wallet": 65}
txn_amounts = [round(max(5.0, float(np.random.exponential(base_txn[m]))), 2) for m in methods]
geos = np.random.choice(["North America", "Western Europe", "Eastern Europe", "Asia-Pacific", "Latin America", "Offshore / High-Risk"], n_txns, p=[0.45, 0.25, 0.10, 0.10, 0.06, 0.04])

risk_scores = []
is_fraud = []
for m, amt, g in zip(methods, txn_amounts, geos):
    score = np.random.beta(2, 7) * 65
    if amt > base_txn[m] * 3.5:
        score += 22
    if g == "Offshore / High-Risk":
        score += 30
    if m == "Web3/Crypto" and amt > 2500:
        score += 18
    score = min(100.0, max(1.0, round(score, 1)))
    risk_scores.append(score)
    is_fraud.append(score > 80.0 and np.random.random() < 0.82)

df_fintech = pd.DataFrame({
    "txn_id": [f"TXN-{500000+i}" for i in range(n_txns)],
    "timestamp": txn_dates,
    "date": [d.date() for d in txn_dates],
    "payment_method": methods,
    "amount": txn_amounts,
    "jurisdiction": geos,
    "risk_score": risk_scores,
    "is_fraud": is_fraud,
    "decision": ["BLOCK" if f else ("FLAG_REVIEW" if s > 65 else "APPROVE") for f, s in zip(is_fraud, risk_scores)],
    "velocity_1h": np.random.poisson(2, n_txns),
    "proxy_ip": np.random.choice([False, True], n_txns, p=[0.92, 0.08])
})
df_fintech.to_parquet(os.path.join(DATA_DIR, "fintech_transactions.parquet"), index=False)


print(">> [4/5] Generating Game LiveOps Data...")
n_players = 12000
first_seen = [datetime(2024, 1, 1) + timedelta(days=int(d)) for d in np.random.uniform(0, 365, n_players)]
levels = np.random.choice(range(1, 51), n_players, p=[0.22] + [0.78/49]*49)
iap_spend = [round(float(np.random.exponential(15.0)), 2) if np.random.random() < 0.26 else 0.0 for _ in range(n_players)]
gold = [int(lvl * np.random.uniform(250, 750) + spend * 600) for lvl, spend in zip(levels, iap_spend)]
retained_d1 = [np.random.random() < 0.72 for _ in levels]
retained_d7 = [r1 and lvl > 4 and np.random.random() < 0.58 for r1, lvl in zip(retained_d1, levels)]
retained_d30 = [r7 and np.random.random() < 0.52 for r7 in retained_d7]

df_gaming = pd.DataFrame({
    "player_id": [f"PLY-{10000+i}" for i in range(n_players)],
    "first_seen": first_seen,
    "date": [d.date() for d in first_seen],
    "level": levels,
    "gold_balance": gold,
    "iap_spend": iap_spend,
    "battlepass_tier": [min(100, int(l * 2)) for l in levels],
    "is_whale": [s > 75.0 for s in iap_spend],
    "retained_d1": retained_d1,
    "retained_d7": retained_d7,
    "retained_d30": retained_d30,
    "channel": np.random.choice(["TikTok Ads", "Unity Ads", "App Store Organic", "Creator Campaign"], n_players, p=[0.38, 0.32, 0.20, 0.10])
})
df_gaming.to_parquet(os.path.join(DATA_DIR, "gaming_telemetry.parquet"), index=False)


print(">> [5/5] Generating HealthTech Telemetry Data...")
n_patients = 5000
age = np.random.normal(56, 15, n_patients).clip(18, 92).astype(int)
risk_cat = np.random.choice(["Low Risk", "Moderate", "High Risk", "Critical Alert"], n_patients, p=[0.46, 0.30, 0.16, 0.08])
heart_rate = [round(np.random.normal(72, 9)) if r != "Critical Alert" else round(np.random.normal(108, 16)) for r in risk_cat]
hrv = [round(max(14, np.random.normal(56 - a*0.32, 11)), 1) for a in age]
spo2 = [round(min(100, max(82, np.random.normal(98, 1.4 if r != "Critical Alert" else 4.2))), 1) for r in risk_cat]
bp_sys = [round(np.random.normal(120, 10)) if r in ["Low Risk", "Moderate"] else round(np.random.normal(155, 18)) for r in risk_cat]
treatment = np.random.choice(["Standard Protocol", "AI Predictive Protocol"], n_patients, p=[0.5, 0.5])
survival = [round(np.random.exponential(20 if t == "AI Predictive Protocol" else 13), 1) for t in treatment]
admit_dates = [datetime(2024, 1, 1) + timedelta(days=int(d)) for d in np.random.uniform(0, 365, n_patients)]

df_health = pd.DataFrame({
    "patient_id": [f"MED-{7000+i}" for i in range(n_patients)],
    "admit_date": admit_dates,
    "date": [d.date() for d in admit_dates],
    "age": age,
    "gender": np.random.choice(["Female", "Male"], n_patients),
    "ward": np.random.choice(["Cardiology", "Neurology", "General ICU", "Oncology", "Step-Down"], n_patients, p=[0.3, 0.2, 0.2, 0.15, 0.15]),
    "risk_category": risk_cat,
    "heart_rate": heart_rate,
    "hrv_ms": hrv,
    "spo2": spo2,
    "bp_systolic": bp_sys,
    "treatment": treatment,
    "survival_months": survival,
    "readmitted_30d": np.random.choice([False, True], n_patients, p=[0.84, 0.16])
})
df_health.to_parquet(os.path.join(DATA_DIR, "health_telemetry.parquet"), index=False)

print(">> [ALL 5 DATASETS GENERATED SUCCESSFULLY!]")
