# projects/gaming/page3_currency.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.theme import render_kpi, render_section_header, render_export_button, get_plotly_layout

def render(df):
    render_section_header("Virtual Currency Economy: Sink vs Source", badge="MACRO ECONOMY", subtitle="Monitoring money supply, gold faucet sources, item sinks, and currency velocity")
    
    total_gold = df["gold_balance"].sum()
    mean_gold = df["gold_balance"].mean()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Circulating Gold Pool", f"{total_gold/1e6:.2f}M Gold", delta="+4.2% MoM", is_positive=True, badge="SUPPLY")
    with c2:
        render_kpi("Sink / Source Ratio", "0.94x", delta="Stable balance (~1.0x)", is_positive=True, badge="RATIO")
    with c3:
        render_kpi("Mean Gold Per Active", f"{mean_gold:,.0f}", delta="+120 gold", is_positive=True, badge="PER CAPITA")
    with c4:
        render_kpi("Virtual Inflation Index", "2.1% / mo", delta="Healthy economy", is_positive=True, badge="INFLATION")
        
    c1, c2 = st.columns([6, 6])
    with c1:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>PRIMARY GOLD FAUCET SOURCES</div>", unsafe_allow_html=True)
        sources = pd.DataFrame({"Source": ["Quest Rewards", "Boss Loot Drops", "PvP Arena Wins", "Battlepass Free", "IAP Gold Packs"], "Share": [38, 25, 18, 12, 7]})
        fig_s = px.pie(sources, values="Share", names="Source", hole=0.6, color_discrete_sequence=["#06b6d4", "#38bdf8", "#818cf8", "#c084fc", "#ec4899"])
        fig_s.update_layout(**get_plotly_layout("gaming", height=300))
        st.plotly_chart(fig_s, use_container_width=True)
    with c2:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #a5f3fc; margin-bottom: 8px;'>PRIMARY GOLD SINKS (DRAINS)</div>", unsafe_allow_html=True)
        sinks = pd.DataFrame({"Sink": ["Gear Upgrades", "Cosmetic Skins", "Consumable Potions", "Auction House Tax", "Guild Expansion"], "Share": [42, 28, 14, 10, 6]})
        fig_sk = px.pie(sinks, values="Share", names="Sink", hole=0.6, color_discrete_sequence=["#ec4899", "#f43f5e", "#fb7185", "#fda4af", "#a855f7"])
        fig_sk.update_layout(**get_plotly_layout("gaming", height=300))
        st.plotly_chart(fig_sk, use_container_width=True)
        
    render_export_button(df[["player_id", "level", "gold_balance", "iap_spend"]].head(500), "virtual_economy_ledger.csv")
