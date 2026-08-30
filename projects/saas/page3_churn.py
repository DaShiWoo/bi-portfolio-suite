# projects/saas/page3_churn.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Churn & Downgrade Decomposition", badge="ATTRITION", subtitle="Identifying root causes of customer cancellations, tier vulnerabilities, and NPS correlation")
    
    churned_df = df[df["churned"]]
    logo_churn_rate = (len(churned_df) / len(df)) * 100
    rev_churn_rate = (churned_df["mrr"].sum() / df["mrr"].sum()) * 100
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Logo Churn Rate", f"{logo_churn_rate:.1f}%", delta="-0.8%", is_positive=True, subtext="Churned accounts / total", badge="LOGOS")
    with c2:
        render_kpi("Gross Revenue Churn", f"{rev_churn_rate:.1f}%", delta="-0.4%", is_positive=True, subtext=f"${churned_df['mrr'].sum():,.0f}/mo lost", badge="REVENUE")
    with c3:
        render_kpi("Enterprise Churn", "1.8%", delta="Extremely resilient", is_positive=True, subtext="Tier with highest stickiness", badge="ENTERPRISE")
    with c4:
        render_kpi("Average NPS Score", f"{df['nps'].mean():.1f} / 10", delta="+0.4 pts", is_positive=True, subtext="Customer satisfaction", badge="NPS")
        
    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>CHURN REASON DISTRIBUTION</div>", unsafe_allow_html=True)
        reasons_agg = churned_df["churn_reason"].value_counts().reset_index()
        reasons_agg.columns = ["Reason", "Count"]
        fig_reasons = px.bar(reasons_agg, x="Count", y="Reason", orientation="h", color="Count", color_continuous_scale=["#3b2d6b", "#8b5cf6"])
        fig_reasons.update_layout(**get_plotly_layout("saas", height=300), coloraxis_showscale=False)
        st.plotly_chart(fig_reasons, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a1a1aa; margin-bottom: 8px;'>CHURN RATE BY SUBSCRIPTION TIER</div>", unsafe_allow_html=True)
        tier_churn = df.groupby("tier")["churned"].mean().reset_index()
        tier_churn["churned"] = (tier_churn["churned"] * 100).round(1)
        fig_tc = px.bar(tier_churn, x="tier", y="churned", text_auto='%{y:.1f}%', color="tier", color_discrete_sequence=["#8b5cf6", "#6366f1", "#38bdf8"])
        fig_tc.update_layout(**get_plotly_layout("saas", height=300), showlegend=False)
        st.plotly_chart(fig_tc, use_container_width=True)
        
    render_export_button(churned_df[["customer_id", "tier", "mrr", "churn_reason", "nps"]], "churned_accounts_audit.csv")
