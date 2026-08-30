"""
tests/test_data_loader.py
Unit tests for core/data_loader.py: caching, schema validation, and data integrity.
"""
import pytest
import pandas as pd
from core.data_loader import (
    load_marketplace_orders,
    load_marketplace_inventory,
    load_saas_subscriptions,
    load_fintech_transactions,
    load_gaming_telemetry,
    load_health_telemetry,
    get_dataset,
    EXPECTED_SCHEMAS,
)


def test_marketplace_orders_schema():
    df = load_marketplace_orders()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    for col in EXPECTED_SCHEMAS["marketplace_orders"]:
        assert col in df.columns, f"Missing column {col}"
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])


def test_marketplace_inventory_schema():
    df = load_marketplace_inventory()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    for col in EXPECTED_SCHEMAS["marketplace_inventory"]:
        assert col in df.columns, f"Missing column {col}"


def test_saas_subscriptions_schema():
    df = load_saas_subscriptions()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    for col in EXPECTED_SCHEMAS["saas_subscriptions"]:
        assert col in df.columns, f"Missing column {col}"


def test_fintech_transactions_schema():
    df = load_fintech_transactions()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    for col in EXPECTED_SCHEMAS["fintech_transactions"]:
        assert col in df.columns, f"Missing column {col}"
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])


def test_gaming_telemetry_schema():
    df = load_gaming_telemetry()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    for col in EXPECTED_SCHEMAS["gaming_telemetry"]:
        assert col in df.columns, f"Missing column {col}"


def test_health_telemetry_schema():
    df = load_health_telemetry()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    for col in EXPECTED_SCHEMAS["health_telemetry"]:
        assert col in df.columns, f"Missing column {col}"


def test_get_dataset_dispatch():
    for name in EXPECTED_SCHEMAS.keys():
        df = get_dataset(name)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    with pytest.raises(KeyError):
        get_dataset("invalid_dataset_name")
