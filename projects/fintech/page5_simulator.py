# projects/fintech/page5_simulator.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Rule Engine Simulator & Precision Tuning", badge="WHAT-IF ENGINE", subtitle="Simulating precision vs recall trade-offs: false positive friction vs blocked fraud revenue")
    
    st.markdown("""
    <div class="what-if-container">
        <span style="font-weight: 700; color: #10b981; font-size: 0.95rem;">🔮 INTERACTIVE WHAT-IF SCENARIO: AUTOMATED BLOCK THRESHOLD</span>
        <div style="font-size: 0.8rem; color: #6ee7b7; margin-top: 4px;">Adjust the automated block cutoff score to evaluate customer friction against fraud prevention:</div>
    </div>
    """, unsafe_allow_html=True)
    
    threshold = st.slider("Automated Block Cutoff Score", min_value=50.0, max_value=95.0, value=80.0, step=1.0)
    
    blocked_txns = df[df["risk_score"] >= threshold]
    blocked_vol = blocked_txns["amount"].sum()
    true_fraud_blocked = blocked_txns[blocked_txns["is_fraud"]]
    false_positives = blocked_txns[~blocked_txns["is_fraud"]]
    
    fp_vol = false_positives["amount"].sum()
    precision = (len(true_fraud_blocked) / len(blocked_txns) * 100) if len(blocked_txns) > 0 else 100
    
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi("Fraud Volume Blocked", f"${true_fraud_blocked['amount'].sum():,.0f}", delta=f"{len(true_fraud_blocked)} attacks prevented", is_positive=True, badge="PREVENTED")
    with c2:
        render_kpi("False Positive Friction", f"${fp_vol:,.0f}", delta=f"{len(false_positives)} legit users blocked", is_positive=False, badge="FRICTION")
    with c3:
        render_kpi("Rule Precision Rate", f"{precision:.1f}%", delta="Target > 92%", is_positive=precision>90, badge="PRECISION")
        
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #6ee7b7; margin-bottom: 8px;'>SIMULATED DECISION WATERFALL AT CUTOFF = " + str(threshold) + "</div>", unsafe_allow_html=True)
    fig_wf = go.Figure(go.Waterfall(
        name="Rule Impact", orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=["Total Transactions", "Approved Legit", "Legit Blocked (FP)", "Fraud Neutralized"],
        textposition="outside",
        y=[len(df), -(len(df)-len(blocked_txns)), -len(false_positives), len(true_fraud_blocked)],
        connector={"line": {"color": "rgba(255,255,255,0.2)"}},
        decreasing={"marker": {"color": "#3b82f6"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#ef4444"}}
    ))
    fig_wf.update_layout(**get_plotly_layout("fintech", height=320))
    st.plotly_chart(fig_wf, use_container_width=True)
    
    render_export_button(pd.DataFrame([{"Cutoff": threshold, "Blocked_Fraud": len(true_fraud_blocked), "False_Positives": len(false_positives), "Precision": precision}]), "threshold_simulation_results.csv")
