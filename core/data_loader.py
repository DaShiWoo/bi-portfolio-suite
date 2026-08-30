"""
core/data_loader.py
Enterprise Data Loading and Caching Layer for BI Portfolio Hub.
Provides cached, validated dataframes with automatic type coercion and schema enforcement.
"""

from typing import Dict, List, Optional
import os
import streamlit as st
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

EXPECTED_SCHEMAS: Dict[str, List[str]] = {
    "marketplace_orders": [
        "order_id", "timestamp", "date", "sku", "category", "amount",
        "status", "channel", "region", "take_rate", "marketplace_fee", "cogs", "profit"
    ],
    "marketplace_inventory": [
        "sku", "category", "stock_units", "daily_velocity", "days_of_inventory",
        "unit_cost", "abc_class", "xyz_class", "stockout_risk"
    ],
    "saas_subscriptions": [
        "customer_id", "signup_date", "date", "cohort", "tier", "mrr",
        "arr", "churned", "churn_reason", "expansion_mrr", "contraction_mrr",
        "channel", "cac", "nps"
    ],
    "fintech_transactions": [
        "txn_id", "timestamp", "date", "payment_method", "amount",
        "jurisdiction", "risk_score", "is_fraud", "decision", "velocity_1h", "proxy_ip"
    ],
    "gaming_telemetry": [
        "player_id", "first_seen", "date", "level", "gold_balance",
        "iap_spend", "battlepass_tier", "is_whale", "retained_d1",
        "retained_d7", "retained_d30", "channel"
    ],
    "health_telemetry": [
        "patient_id", "admit_date", "date", "age", "gender", "ward",
        "risk_category", "heart_rate", "hrv_ms", "spo2", "bp_systolic",
        "treatment", "survival_months", "readmitted_30d"
    ],
}


def _validate_schema(df: pd.DataFrame, dataset_name: str) -> None:
    """Validate that expected columns exist in the loaded dataframe."""
    expected = EXPECTED_SCHEMAS.get(dataset_name)
    if not expected:
        return
    missing = [col for col in expected if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset '{dataset_name}' missing expected columns: {missing}")


@st.cache_data(show_spinner=False)
def load_marketplace_orders() -> pd.DataFrame:
    """Load and prepare marketplace orders dataset."""
    path = os.path.join(DATA_DIR, "marketplace_orders.parquet")
    df = pd.read_parquet(path)
    _validate_schema(df, "marketplace_orders")
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


@st.cache_data(show_spinner=False)
def load_marketplace_inventory() -> pd.DataFrame:
    """Load marketplace inventory dataset."""
    path = os.path.join(DATA_DIR, "marketplace_inventory.parquet")
    df = pd.read_parquet(path)
    _validate_schema(df, "marketplace_inventory")
    return df


@st.cache_data(show_spinner=False)
def load_saas_subscriptions() -> pd.DataFrame:
    """Load and prepare SaaS subscriptions dataset."""
    path = os.path.join(DATA_DIR, "saas_subscriptions.parquet")
    df = pd.read_parquet(path)
    _validate_schema(df, "saas_subscriptions")
    if "signup_date" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["signup_date"]):
        df["signup_date"] = pd.to_datetime(df["signup_date"])
    return df


@st.cache_data(show_spinner=False)
def load_fintech_transactions() -> pd.DataFrame:
    """Load and prepare fintech transactions dataset."""
    path = os.path.join(DATA_DIR, "fintech_transactions.parquet")
    df = pd.read_parquet(path)
    _validate_schema(df, "fintech_transactions")
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


@st.cache_data(show_spinner=False)
def load_gaming_telemetry() -> pd.DataFrame:
    """Load and prepare gaming telemetry dataset."""
    path = os.path.join(DATA_DIR, "gaming_telemetry.parquet")
    df = pd.read_parquet(path)
    _validate_schema(df, "gaming_telemetry")
    if "first_seen" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["first_seen"]):
        df["first_seen"] = pd.to_datetime(df["first_seen"])
    return df


@st.cache_data(show_spinner=False)
def load_health_telemetry() -> pd.DataFrame:
    """Load and prepare health telemetry dataset."""
    path = os.path.join(DATA_DIR, "health_telemetry.parquet")
    df = pd.read_parquet(path)
    _validate_schema(df, "health_telemetry")
    if "admit_date" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["admit_date"]):
        df["admit_date"] = pd.to_datetime(df["admit_date"])
    return df


def get_dataset(name: str) -> pd.DataFrame:
    """Dispatch dataset loader by name."""
    loaders = {
        "marketplace_orders": load_marketplace_orders,
        "marketplace_inventory": load_marketplace_inventory,
        "saas_subscriptions": load_saas_subscriptions,
        "fintech_transactions": load_fintech_transactions,
        "gaming_telemetry": load_gaming_telemetry,
        "health_telemetry": load_health_telemetry,
    }
    if name not in loaders:
        raise KeyError(f"Unknown dataset name: {name}. Available: {list(loaders.keys())}")
    return loaders[name]()
