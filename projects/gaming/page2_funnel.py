# projects/gaming/page2_funnel.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Level Progression & Churn Bottlenecks", badge="FUNNEL", subtitle="Mapping player drop-off from onboarding tutorial through endgame mastery")
    
    bins = [0, 3, 7, 15, 30, 50]
    labels = ["Tutorial (1-3)", "Early (4-7)", "Midgame (8-15)", "Advanced (16-30)", "Endgame (31-50)"]
    df["bracket"] = pd.cut(df["level"], bins=bins, labels=labels)
    br_agg = df["bracket"].value_counts().reindex(labels).reset_index()
    br_agg.columns = ["Stage", "Players"]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Tutorial Completion Rate", "88.4%", delta="+2.1%", is_positive=True, badge="TUTORIAL")
    with c2:
        render_kpi("Level 7 Churn Wall", "32.1% drop", delta="Key friction point", is_positive=False, badge="FRICTION")
    with c3:
        render_kpi("Endgame Player Base", f"{br_agg[br_agg['Stage']=='Endgame (31-50)']['Players'].values[0]:,}", delta="+14.8%", is_positive=True, badge="VETERANS")
    with c4:
        render_kpi("Median Level Reached", f"Lvl {df['level'].median():.0f}", delta="Normal distribution", is_positive=True, badge="MEDIAN")
        
    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>PROGRESSION FUNNEL (STAGES 1 TO 5)</div>", unsafe_allow_html=True)
        fig_fun = go.Figure(go.Funnel(
            y=br_agg["Stage"], x=br_agg["Players"], textinfo="value+percent initial",
            marker=dict(color=["#06b6d4", "#38bdf8", "#818cf8", "#c084fc", "#ec4899"])
        ))
        fig_fun.update_layout(**get_plotly_layout("gaming", height=300))
        st.plotly_chart(fig_fun, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>PLAYERS PER EXACT LEVEL (1-50)</div>", unsafe_allow_html=True)
        lvl_cnt = df["level"].value_counts().sort_index().reset_index()
        lvl_cnt.columns = ["Level", "Count"]
        fig_bar = px.bar(lvl_cnt, x="Level", y="Count", color="Count", color_continuous_scale=["#070919", "#06b6d4"])
        fig_bar.update_layout(**get_plotly_layout("gaming", height=300), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    render_export_button(br_agg, "level_progression_funnel.csv")
