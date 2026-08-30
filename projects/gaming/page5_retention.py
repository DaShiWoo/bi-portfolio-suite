# projects/gaming/page5_retention.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout
from core.filters import build_gaming_filters, check_empty_state


def render(df: pd.DataFrame) -> None:
    """Render the Retention Benchmark Simulator page."""
    if check_empty_state(df, "players"):
        return
    df_f = df

    render_section_header(
        "Retention Benchmark Simulator",
        badge="WHAT-IF SIMULATOR",
        subtitle="Interactive game tuning: simulate onboarding difficulty vs D1, D7, and D30 cohort curves",
    )

    # Compute real baseline rates from filtered cohort
    n = len(df_f)
    base_d1 = df_f["retained_d1"].mean() * 100 if ("retained_d1" in df_f.columns and n > 0) else 70.0
    base_d7 = df_f["retained_d7"].mean() * 100 if n > 0 else 42.0
    base_d30 = df_f["retained_d30"].mean() * 100 if n > 0 else 21.0
    base_d3 = (base_d1 + base_d7) / 2
    base_d14 = (base_d7 + base_d30) / 2 * 1.1
    base_d21 = (base_d7 + base_d30) / 2 * 0.9

    st.markdown("""
    <div class="what-if-container">
        <span style="font-weight: 700; color: #06b6d4; font-size: 0.95rem;">🔮 INTERACTIVE WHAT-IF SCENARIO: ONBOARDING FRICTION OPTIMIZATION</span>
        <div style="font-size: 0.8rem; color: #a5f3fc; margin-top: 4px;">Model how reducing early-game friction shifts D1, D7, and D30 cohort retention curves:</div>
    </div>
    """, unsafe_allow_html=True)

    d1_boost = st.slider("Simulated D1 Retention Boost (+%)", min_value=0.0, max_value=15.0, value=6.0, step=0.5)

    sim_d1 = min(95.0, base_d1 + d1_boost)
    sim_d7 = min(80.0, base_d7 + (d1_boost * 0.75))
    sim_d30 = min(60.0, base_d30 + (d1_boost * 0.55))
    sim_d3 = (sim_d1 + sim_d7) / 2
    sim_d14 = (sim_d7 + sim_d30) / 2 * 1.1
    sim_d21 = (sim_d7 + sim_d30) / 2 * 0.9

    cohort_size_label = f"Filtered cohort: {n:,} players"
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi("Baseline D1 Retention", f"{base_d1:.1f}%", delta=cohort_size_label, is_positive=True, badge="ACTUAL D1")
    with c2:
        render_kpi("Baseline D7 Retention", f"{base_d7:.1f}%", delta=f"D30 baseline: {base_d30:.1f}%", is_positive=True, badge="ACTUAL D7")
    with c3:
        render_kpi("Simulated D1 Retention", f"{sim_d1:.1f}%", delta=f"+{d1_boost:.1f}% boost applied", is_positive=True, badge="SIM D1")

    days = ["D1", "D3", "D7", "D14", "D21", "D30"]
    base_curve = [base_d1, base_d3, base_d7, base_d14, base_d21, base_d30]
    sim_curve = [sim_d1, sim_d3, sim_d7, sim_d14, sim_d21, sim_d30]
    lifts = [round(s - b, 1) for s, b in zip(sim_curve, base_curve)]

    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>SIMULATED RETENTION CURVE TRAJECTORY</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=base_curve, name="Actual Baseline (Filtered)", line=dict(color="rgba(255,255,255,0.4)", width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=days, y=sim_curve, name="Optimized Retention Curve", line=dict(color="#06b6d4", width=3), marker=dict(size=8, color="#ec4899"), fill="tonexty", fillcolor="rgba(6, 182, 212, 0.15)"))
        fig.update_layout(**get_plotly_layout("gaming", height=300))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>RETENTION LIFT BY MILESTONE (+% PTS)</div>", unsafe_allow_html=True)
        fig_lift = go.Figure(go.Bar(
            x=days, y=lifts, marker_color="#ec4899",
            text=[f"+{v:.1f}%" for v in lifts], textposition="outside",
        ))
        fig_lift.update_layout(**get_plotly_layout("gaming", height=300))
        st.plotly_chart(fig_lift, use_container_width=True)

    render_export_button(
        pd.DataFrame({"Day": days, "Baseline": [round(v, 1) for v in base_curve], "Simulated": [round(v, 1) for v in sim_curve]}),
        "retention_simulation_export.csv",
    )
