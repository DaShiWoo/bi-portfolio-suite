# projects/gaming/page2_funnel.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    # ── Sidebar Filters ───────────────────────────────────────────────────────
    with st.sidebar:
        with st.expander("🔍 FILTERS", expanded=True):
            channels = st.multiselect(
                "Acquisition Channel",
                options=df["channel"].unique().tolist(),
                default=df["channel"].unique().tolist(),
            )
            level_range = st.slider("Player Level Range", 1, 50, (1, 50))
            payers_only = st.checkbox("Paying Players Only", value=False)

    df_f = df[df["channel"].isin(channels) & df["level"].between(level_range[0], level_range[1])]
    if payers_only:
        df_f = df_f[df_f["iap_spend"] > 0]

    render_section_header(
        "Level Progression & Churn Bottlenecks",
        badge="FUNNEL",
        subtitle="Mapping player drop-off from onboarding tutorial through endgame mastery",
    )

    bins = [0, 3, 7, 15, 30, 50]
    labels = ["Tutorial (1-3)", "Early (4-7)", "Midgame (8-15)", "Advanced (16-30)", "Endgame (31-50)"]
    df_f = df_f.copy()
    df_f["bracket"] = pd.cut(df_f["level"], bins=bins, labels=labels)
    br_agg = df_f["bracket"].value_counts().reindex(labels).reset_index()
    br_agg.columns = ["Stage", "Players"]
    br_agg["Players"] = br_agg["Players"].fillna(0).astype(int)

    top_stage = br_agg.iloc[0]["Players"]
    bottom_stage = br_agg.iloc[-1]["Players"]
    overall_conv = (bottom_stage / top_stage * 100) if top_stage > 0 else 0.0
    median_lvl = df_f["level"].median()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        tut_count = br_agg[br_agg["Stage"] == "Tutorial (1-3)"]["Players"].values[0]
        early_count = br_agg[br_agg["Stage"] == "Early (4-7)"]["Players"].values[0]
        tut_conv = (early_count / tut_count * 100) if tut_count > 0 else 0.0
        render_kpi("Tutorial Completion Rate", f"{tut_conv:.1f}%", delta="+2.1%", is_positive=True, badge="TUTORIAL")
    with c2:
        mid_count = br_agg[br_agg["Stage"] == "Midgame (8-15)"]["Players"].values[0]
        churn_wall = ((early_count - mid_count) / early_count * 100) if early_count > 0 else 0.0
        render_kpi("Level 7 Churn Wall", f"{churn_wall:.1f}% drop", delta="Key friction point", is_positive=False, badge="FRICTION")
    with c3:
        eg_count = br_agg[br_agg["Stage"] == "Endgame (31-50)"]["Players"].values[0]
        render_kpi("Endgame Player Base", f"{eg_count:,}", delta=f"{overall_conv:.1f}% funnel conv.", is_positive=True, badge="VETERANS")
    with c4:
        render_kpi("Median Level Reached", f"Lvl {median_lvl:.0f}", delta="Cohort median", is_positive=True, badge="MEDIAN")

    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>PROGRESSION FUNNEL (STAGES 1 TO 5)</div>", unsafe_allow_html=True)
        fig_fun = go.Figure(go.Funnel(
            y=br_agg["Stage"], x=br_agg["Players"], textinfo="value+percent initial",
            marker=dict(color=["#06b6d4", "#38bdf8", "#818cf8", "#c084fc", "#ec4899"]),
        ))
        fig_fun.update_layout(**get_plotly_layout("gaming", height=300))
        st.plotly_chart(fig_fun, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>PLAYERS PER EXACT LEVEL (1-50)</div>", unsafe_allow_html=True)
        lvl_cnt = df_f["level"].value_counts().sort_index().reset_index()
        lvl_cnt.columns = ["Level", "Count"]
        fig_bar = px.bar(lvl_cnt, x="Level", y="Count", color="Count", color_continuous_scale=["#070919", "#06b6d4"])
        fig_bar.update_layout(**get_plotly_layout("gaming", height=300), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    render_export_button(br_agg, "level_progression_funnel.csv")
