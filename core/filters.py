"""
core/filters.py
Declarative, Reusable Filter Engine & Empty-State Manager for BI Portfolio Hub.
Eliminates code duplication across all 25 analytics pages.
"""

from typing import List, Optional, Tuple, Dict, Any
import streamlit as st
import pandas as pd


def render_filter_status(filtered_count: int, total_count: int, entity_name: str = "records") -> None:
    """Render a styled banner showing filter count and retention percentage with rock-solid flex alignment."""
    pct = (filtered_count / total_count * 100) if total_count > 0 else 0.0
    st.sidebar.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 8px 12px;
            margin-top: 12px;
            margin-bottom: 14px;
            font-size: 0.78rem;
            color: #94a3b8;
            box-sizing: border-box;
        ">
            <div style="display: flex; align-items: center; gap: 6px; min-width: 0; overflow: hidden;">
                <span style="color: #60a5fa; font-size: 0.82rem; line-height: 1; flex-shrink: 0;">⚡</span>
                <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    <strong style="color: #f8fafc; font-weight: 600;">Active Slice:</strong>
                    <span style="color: #cbd5e1; margin-left: 2px;">{filtered_count:,} / {total_count:,}</span>
                </span>
            </div>
            <span style="
                background: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.28);
                color: #34d399;
                font-weight: 700;
                font-size: 0.72rem;
                padding: 2px 7px;
                border-radius: 6px;
                white-space: nowrap;
                flex-shrink: 0;
            ">{pct:.1f}%</span>
        </div>
        """,
        unsafe_allow_html=True
    )



def check_empty_state(df_f: pd.DataFrame, entity_name: str = "records") -> bool:
    """
    Check if filtered dataframe is empty.
    If empty, renders a clean, user-friendly callout and returns True (to stop execution).
    """
    if len(df_f) == 0:
        st.markdown(
            f"""
            <div style="
                background: rgba(239, 68, 68, 0.08);
                border: 1px solid rgba(239, 68, 68, 0.25);
                border-radius: 12px;
                padding: 24px;
                margin: 20px 0;
                text-align: center;
            ">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">🔍 No {entity_name} Found</div>
                <div style="font-size: 0.92rem; color: #fca5a5;">
                    The current combination of sidebar filters resulted in zero matching records.<br>
                    Please broaden your date range, select additional categories, or reset sliders.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return True
    return False


def build_marketplace_filters(
    df: pd.DataFrame,
    key_prefix: str = "mkt"
) -> pd.DataFrame:
    """Standardized sidebar filter block for Marketplace pages."""
    with st.sidebar:
        with st.expander("🔍 MARKETPLACE FILTERS", expanded=True):
            min_date = df["timestamp"].dt.date.min()
            max_date = df["timestamp"].dt.date.max()
            date_range = st.date_input(
                "Date Range",
                value=[min_date, max_date],
                key=f"{key_prefix}_date"
            )

            all_cats = sorted(df["category"].unique().tolist())
            categories = st.multiselect(
                "Categories",
                options=all_cats,
                default=all_cats,
                key=f"{key_prefix}_cat"
            )

            all_channels = sorted(df["channel"].unique().tolist())
            channels = st.multiselect(
                "Acquisition Channels",
                options=all_channels,
                default=all_channels,
                key=f"{key_prefix}_chan"
            )

            all_regions = sorted(df["region"].unique().tolist())
            regions = st.multiselect(
                "Regions",
                options=all_regions,
                default=all_regions,
                key=f"{key_prefix}_reg"
            )

    d0 = pd.to_datetime(date_range[0]) if len(date_range) >= 1 else pd.to_datetime(min_date)
    d1 = pd.to_datetime(date_range[1]) if len(date_range) >= 2 else pd.to_datetime(max_date)

    mask = (
        (df["timestamp"] >= d0) &
        (df["timestamp"] <= d1 + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)) &
        df["category"].isin(categories) &
        df["channel"].isin(channels) &
        df["region"].isin(regions)
    )
    df_f = df[mask].copy()
    render_filter_status(len(df_f), len(df), "orders")
    return df_f


def build_saas_filters(
    df: pd.DataFrame,
    key_prefix: str = "saas"
) -> pd.DataFrame:
    """Standardized sidebar filter block for SaaS pages."""
    with st.sidebar:
        with st.expander("🔍 SAAS COHORT FILTERS", expanded=True):
            all_tiers = sorted(df["tier"].unique().tolist())
            tiers = st.multiselect(
                "Subscription Tier",
                options=all_tiers,
                default=all_tiers,
                key=f"{key_prefix}_tier"
            )

            all_channels = sorted(df["channel"].unique().tolist())
            channels = st.multiselect(
                "Acquisition Channel",
                options=all_channels,
                default=all_channels,
                key=f"{key_prefix}_chan"
            )

            status_opt = st.radio(
                "Customer Status",
                ["All Customers", "Active Only", "Churned Only"],
                index=0,
                key=f"{key_prefix}_stat"
            )

    mask = df["tier"].isin(tiers) & df["channel"].isin(channels)
    if status_opt == "Active Only":
        mask = mask & (~df["churned"])
    elif status_opt == "Churned Only":
        mask = mask & df["churned"]

    df_f = df[mask].copy()
    render_filter_status(len(df_f), len(df), "subscribers")
    return df_f


def build_fintech_filters(
    df: pd.DataFrame,
    key_prefix: str = "fin"
) -> pd.DataFrame:
    """Standardized sidebar filter block for Fintech pages."""
    with st.sidebar:
        with st.expander("🔍 AML / RISK FILTERS", expanded=True):
            all_juris = sorted(df["jurisdiction"].unique().tolist())
            jurisdictions = st.multiselect(
                "Jurisdictions",
                options=all_juris,
                default=all_juris,
                key=f"{key_prefix}_juri"
            )

            all_methods = sorted(df["payment_method"].unique().tolist())
            payment_methods = st.multiselect(
                "Payment Rails",
                options=all_methods,
                default=all_methods,
                key=f"{key_prefix}_pm"
            )

            risk_range = st.slider(
                "Risk Score Range",
                0, 100, (0, 100),
                key=f"{key_prefix}_risk"
            )

    mask = (
        df["jurisdiction"].isin(jurisdictions) &
        df["payment_method"].isin(payment_methods) &
        (df["risk_score"] >= risk_range[0]) &
        (df["risk_score"] <= risk_range[1])
    )
    df_f = df[mask].copy()
    render_filter_status(len(df_f), len(df), "transactions")
    return df_f


def build_gaming_filters(
    df: pd.DataFrame,
    key_prefix: str = "game"
) -> pd.DataFrame:
    """Standardized sidebar filter block for Gaming pages."""
    with st.sidebar:
        with st.expander("🔍 LIVEOPS FILTERS", expanded=True):
            all_channels = sorted(df["channel"].unique().tolist())
            channels = st.multiselect(
                "Acquisition Channel",
                options=all_channels,
                default=all_channels,
                key=f"{key_prefix}_chan"
            )

            level_range = st.slider(
                "Player Level Range",
                1, 50, (1, 50),
                key=f"{key_prefix}_lvl"
            )

            payers_only = st.checkbox(
                "Paying Players Only (Whales & Spenders)",
                value=False,
                key=f"{key_prefix}_pay"
            )

    mask = (
        df["channel"].isin(channels) &
        (df["level"] >= level_range[0]) &
        (df["level"] <= level_range[1])
    )
    if payers_only:
        mask = mask & (df["iap_spend"] > 0)

    df_f = df[mask].copy()
    render_filter_status(len(df_f), len(df), "players")
    return df_f


def build_healthtech_filters(
    df: pd.DataFrame,
    key_prefix: str = "health"
) -> pd.DataFrame:
    """Standardized sidebar filter block for HealthTech pages."""
    with st.sidebar:
        with st.expander("🔍 CLINICAL WARD FILTERS", expanded=True):
            all_wards = sorted(df["ward"].unique().tolist())
            wards = st.multiselect(
                "Clinical Ward",
                options=all_wards,
                default=all_wards,
                key=f"{key_prefix}_ward"
            )

            all_risks = sorted(df["risk_category"].unique().tolist())
            risk_cats = st.multiselect(
                "Acuity Level",
                options=all_risks,
                default=all_risks,
                key=f"{key_prefix}_risk"
            )

            min_age = int(df["age"].min())
            max_age = int(df["age"].max())
            age_range = st.slider(
                "Patient Age Range",
                min_age, max_age, (min_age, max_age),
                key=f"{key_prefix}_age"
            )

    mask = (
        df["ward"].isin(wards) &
        df["risk_category"].isin(risk_cats) &
        (df["age"] >= age_range[0]) &
        (df["age"] <= age_range[1])
    )
    df_f = df[mask].copy()
    render_filter_status(len(df_f), len(df), "patients")
    return df_f
