# Executive BI Analytics Portfolio Suite (5 Verticals)

Production-grade multi-industry BI analytics suite built with **Streamlit**, **Plotly**, **DuckDB**, and **Apache Parquet**. Features 5 distinct visual design languages (Glassmorphism, Linear/Stripe, Bloomberg Terminal, Cyber Neon, Clinical Teal) in a single unified web application.

---

## 5 Analytical Verticals & Design Themes

| Domain | Visual Design Language | Key Metrics & Visualizations |
|---|---|---|
| **1. Marketplace & E-Commerce** | Vercel Monochrome & Electric Amber | GMV, Net Revenue, Take Rate %, Order Funnel, Regional Share |
| **2. B2B SaaS & Subscriptions** | Linear App Dark & Stripe Royal Indigo | MRR/ARR, NRR Cohort Heatmap, Churn by Tier, Expansion Revenue, CAC Payback |
| **3. Fintech & Anti-Fraud** | Bloomberg Terminal Dark & Emerald/Gold | Live Volume, Anomaly Scatter, Multi-Vector Risk Radar, Real-Time Ledger |
| **4. Game LiveOps & Virtual Economy**| Cyber Neon Arcade (Cyan & Magenta) | DAU/MAU Stickiness, Level Drop-off Funnel, Virtual Currency Sink vs Source |
| **5. HealthTech & Clinical Vitals** | Dark Teal & Mint Hospital Command | Kaplan-Meier Survival Curves, HRV Resilience, SpO2 & Heart Rate Density |

---

## Architecture & Single Source of Truth

- **In-Memory OLAP:** High-performance DuckDB query execution directly over columnar Parquet files.
- **Micro-Footprint:** Total storage for all 5 datasets is **< 3 MB**, enabling instant page transitions and lightweight free-tier deployment.
- **Custom UI Engine (`core/theme.py`):** Dynamic CSS injection for glassmorphic cards, sparkline metrics, badge chips, and Plotly layout synchronization.

---

## Quick Start (Local)

### Windows (1-Click):
Double-click `run.bat`. The script will detect Python, prepare datasets, and launch the dashboard in your default browser.

### Manual CLI:
```bash
pip install -r requirements.txt
python generate_all_data.py
streamlit run hub.py
```

---

## 100% Free Cloud Deployment (Streamlit Community Cloud)

1. Push this repository to **GitHub** (public repo).
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub account, select this repository, and set `Main file path` to **`hub.py`**.
4. Click **Deploy** — your portfolio will be live at a permanent public URL with 5 switchable projects!
