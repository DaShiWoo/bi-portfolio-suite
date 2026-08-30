"""
tests/test_filters.py
Unit tests for core/filters.py: empty-state checks, filter masks, and edge-case resilience.
"""
import pytest
import pandas as pd
import numpy as np
from core.filters import check_empty_state
from core.data_loader import (
    load_marketplace_orders,
    load_saas_subscriptions,
    load_fintech_transactions,
    load_gaming_telemetry,
    load_health_telemetry,
)


def test_empty_state_detection():
    empty_df = pd.DataFrame({"col": []})
    non_empty_df = pd.DataFrame({"col": [1, 2, 3]})
    
    assert check_empty_state(empty_df, "records") is True
    assert check_empty_state(non_empty_df, "records") is False


def test_marketplace_filtering_logic():
    df = load_marketplace_orders()
    selected_cats = ["Electronics", "Fashion"]
    selected_regions = ["North America"]
    
    mask = df["category"].isin(selected_cats) & df["region"].isin(selected_regions)
    df_f = df[mask]
    assert len(df_f) > 0
    assert set(df_f["category"].unique()).issubset(set(selected_cats))
    assert set(df_f["region"].unique()).issubset(set(selected_regions))


def test_saas_churn_filtering_logic():
    df = load_saas_subscriptions()
    active_df = df[~df["churned"]]
    churned_df = df[df["churned"]]
    
    assert len(active_df) + len(churned_df) == len(df)
    assert not active_df["churned"].any()
    assert churned_df["churned"].all()


def test_fintech_risk_score_bounds():
    df = load_fintech_transactions()
    min_score, max_score = 30, 75
    mask = (df["risk_score"] >= min_score) & (df["risk_score"] <= max_score)
    df_f = df[mask]
    
    assert len(df_f) > 0
    assert df_f["risk_score"].min() >= min_score
    assert df_f["risk_score"].max() <= max_score


def test_gaming_payers_filtering():
    df = load_gaming_telemetry()
    payers_df = df[df["iap_spend"] > 0]
    free_df = df[df["iap_spend"] == 0]
    
    assert len(payers_df) + len(free_df) == len(df)
    assert (payers_df["iap_spend"] > 0).all()


def test_healthtech_age_and_ward_filtering():
    df = load_health_telemetry()
    min_age, max_age = 40, 70
    selected_wards = ["ICU-A", "Cardiology"]
    mask = df["ward"].isin(selected_wards) & (df["age"] >= min_age) & (df["age"] <= max_age)
    df_f = df[mask]
    
    assert len(df_f) > 0
    assert df_f["age"].min() >= min_age
    assert df_f["age"].max() <= max_age
    assert set(df_f["ward"].unique()).issubset(set(selected_wards))
