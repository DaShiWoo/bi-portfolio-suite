# projects/saas/page2_nrr.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Net Revenue Retention (NRR) Cohort Matrix", badge="EXPANSION", subtitle="12x12 cohort progression tracking net expansion, upselling, and retention compounding")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Overall Net Revenue Retention", "116.4%", delta="+4.2% YoY", is_positive=True, subtext="Expansion > Churn", badge="NRR")
    with c2:
        render_kpi("Gross Revenue Retention", "92.8%", delta="+1.1%", is_positive=True, subtext="Excluding upsell expansion", badge="GRR")
    with c3:
        render_kpi("Annual Logo Retention", "88.5%", delta="+2.5%", is_positive=True, subtext="11.5% Annual Logo Churn", badge="LOGOS")
    with c4:
        render_kpi("Expansion Contribution", "$48.2k/mo", delta="+18.9%", is_positive=True, subtext="Cross-sell and seat expansion", badge="UPSELL")
        
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    cohort_matrix = []
    for i in range(len(months)):
        row = []
        for j in range(len(months)):
            if j < i:
                row.append(None)
            elif j == i:
                row.append(100.0)
            else:
                diff = j - i
                val = 100.0 + (diff * 3.1) - (diff * 0.9) + np.sin(diff)*1.5
                row.append(round(val, 1))
        cohort_matrix.append(row)
        
    fig_heat = px.imshow(
        cohort_matrix,
        x=[f"M+{k}" for k in range(len(months))],
        y=[f"{m} 2024" for m in months],
        color_continuous_scale=[[0, "#0b0d17"], [0.5, "#3b2d6b"], [1, "#8b5cf6"]],
        text_auto=True,
        aspect="auto"
    )
    fig_heat.update_layout(**get_plotly_layout("saas", height=350))
    fig_heat.update_coloraxes(showscale=False)
    st.plotly_chart(fig_heat, use_container_width=True)
    
    df_cohort_export = pd.DataFrame(cohort_matrix, index=months, columns=[f"M+{k}" for k in range(len(months))])
    render_export_button(df_cohort_export.reset_index(), "nrr_cohort_matrix.csv")
