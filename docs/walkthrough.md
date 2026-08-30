# Enterprise BI Analytics Portfolio Suite (25 Pages Total)

Полноценная представительская BI-система корпоративного уровня из **5 индустрий**, каждая из которых содержит **ровно 5 глубоких аналитических страниц** (суммарно **25 уникальных дашбордов**) на стеке **Streamlit + Plotly + DuckDB/Parquet** с двухуровневой навигацией, кастомным Glassmorphism-дизайном, кнопками экспорта в CSV и интерактивными What-If симуляторами.

**Директория проекта:** `C:\Users\danja\.gemini\antigravity\scratch\bi_portfolio_hub`

---

## Карта 25 аналитических страниц

### 🛍️ Проект 1: Marketplace & E-Commerce (Стиль: Vercel & Amber)
1. **📊 1. Executive Macro Overview** — GMV (\$1.3M+), Net Revenue, Take Rate (15%), операционная маржа, динамика GMV vs Revenue.
2. **📦 2. Orders & Fulfillment Operations** — Тепловая карта пиковых часов продаж (день недели vs час суток), воронка статусов заказов, логистика.
3. **🎯 3. Marketing Attribution & ACoS** — Ad Spend vs Attributed GMV (Scatter), Blended ROAS (12.2x), ACoS (ДРР 8.2%), эффективность каналов.
4. **🏬 4. Inventory & ABC/XYZ Matrix** — Матрица классификации номенклатуры 3x3, Days of Inventory (DOI), радар товаров с риском Out-of-Stock (< 14 дней).
5. **💰 5. Unit Economics & What-If** — Водопадная диаграмма (Waterfall) маржи единицы заказа, **What-If слайдер изменения комиссии маркетплейса** с расчетом изменения годовой выручки.

---

### ⚡ Проект 2: B2B SaaS Subscriptions (Стиль: Linear & Royal Indigo)
1. **📈 1. MRR & ARR Growth Velocity** — MRR bridge (New Logo, Expansion, Contraction, Churned), Quick Ratio, разбивка MRR по тарифам.
2. **🔄 2. NRR & Cohort Retention** — Полная 12x12 матрица когортного удержания выручки (Heatmap), динамика экспансии и чистый отток.
3. **📉 3. Churn & Downgrades** — Logo Churn vs Gross Revenue Churn, частотный анализ причин оттока, уязвимость тарифов, корреляция с NPS.
4. **🎯 4. Acquisition Cost & Payback** — CAC по каналам привлечения, скорость окупаемости (Payback Period в месяцах), LTV:CAC мультипликатор.
5. **🔮 5. What-If Scenario Forecast** — **Интерактивный слайдер оптимизации оттока (-1..-4%) и экспансии (+1..-5%)** с 24-месячным прогнозом сложного роста ARR.

---

### 🛡️ Проект 3: Fintech & Anti-Fraud Defense (Стиль: Bloomberg & Emerald)
1. **🛡️ 1. Live Threat Command** — 24h объем транзакций (\$89M+), предотвращенный ущерб, автоматические блокировки, очередь ручного комплаенса.
2. **🕵️ 2. Anomaly Investigation** — Скаттер-плот аномалий сумм против скоринга риска, пороги авто-блока (>80.0), 6-векторный радар угроз.
3. **💳 3. Payment Channels & Rails** — Карты vs Wire vs Web3/Crypto, конверсия шлюзов, уровень чарджбэков, сравнительный риск платежных рельсов.
4. **🌍 4. Geolocation Risk Matrix** — Трансграничные расчеты, офшорные и санкционные юрисдикции, проникновение анонимных прокси/VPN.
5. **⚙️ 5. Rule Engine Simulator** — **Интерактивный слайдер порога авто-блокировки** с балансировкой ложных срабатываний (False Positives) против заблокированного фрода.

---

### 🎮 Проект 4: Game LiveOps & Economy (Стиль: Cyber Neon Arcade)
1. **🎮 1. Player Engagement & DAU/MAU** — DAU/MAU Stickiness ratio (38%), сессии в день, каналы привлечения игроков, кривые D1..D30.
2. **🧗 2. Level Progression & Churn Funnel** — Воронка оттока на уровнях 1–50, выявление критических точек дроп-оффа (бутылочные горлышки онбординга).
3. **🪙 3. Virtual Currency Sink vs Source** — Макроэкономический баланс виртуального золота, источники притока (фаусеты) против сливов (синки), индекс инфляции.
4. **🛒 4. Monetization & Whale Analytics** — Сегментация донатеров (Free, Minnow, Dolphin, Whale), вклад китов в выручку, конверсия в Battlepass.
5. **⏱️ 5. Retention Benchmark Simulator** — **Интерактивный слайдер сложности онбординга** с симуляцией сдвига когортных кривых D1, D7 и D30.

---

### 🩺 Проект 5: HealthTech & Clinical Vitals (Стиль: Dark Teal Clinical)
1. **🏥 1. Clinical ICU Telemetry** — Активный стационар, критические алерты декомпенсации, средний SpO2, вариабельность пульса (HRV), загрузка палат.
2. **💓 2. Vitals Density & Biomarkers** — Плотность распределения систолического давления, скаттер SpO2 vs частота пульса, маркеры гипоксии.
3. **💊 3. Treatment Efficacy & Survival** — **Кривые выживаемости Каплана-Мейера (36 месяцев)**: сравнительный анализ протокола с предиктивным ИИ против стандарта.
4. **⚠️ 4. Patient Risk Stratification** — Кластеризация когорт по степеням риска, возрастные уязвимости, распределение декомпенсации по отделениям.
5. **📋 5. Cohort Explorer & Discharge Simulator** — **Интерактивный слайдер безопасного порога выписки SpO2** с расчетом высвобождения коек и риска повторной госпитализации.

---

## Архитектура и запуск

- **Двухуровневая навигация:** Уровень 1 (в боковой панели) меняет индустрию и динамически инжектирует тему оформления. Уровень 2 (вкладки в верхней части) переключает ровно 5 страниц.
- **Интерактивность:** Каждая страница оснащена кнопкой **`📥 Export Slice to CSV`** (`st.download_button`).
- **Сверхкомпактность:** Все 5 Parquet-датасетов суммарно занимают **меньше 3 МБ**.

### Локальный запуск:
Двойной клик по:
`C:\Users\danja\.gemini\antigravity\scratch\bi_portfolio_hub\run.bat`

### 1-Click Деплой на Streamlit Community Cloud (100% бесплатно):
Запушить папку репозитория на GitHub и на [share.streamlit.io](https://share.streamlit.io) указать файл `hub.py`.
