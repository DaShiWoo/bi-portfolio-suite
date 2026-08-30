# План реализации: Премиум BI Portfolio Hub (5 проектов)

Создание единого представительского хаба из 5 аналитических систем в разных индустриях с уникальным визуальным стилем (Linear / Stripe / Bloomberg / Neon / Clean Teal) и экстремальной экономией токенов.

---

## 1. Архитектура хаба и дизайн-системы

### Расположение:
`C:\Users\danja\.gemini\antigravity\scratch\bi_portfolio_hub`

### Дизайн-система (`core/theme.py`):
Вместо блеклого дефолтного Streamlit создается движок стилей:
- **Glassmorphism & Shadows:** полупрозрачные карточки с мягкой обводкой `border: 1px solid rgba(255,255,255,0.08)` и эффектом блюра.
- **KPI-карточки со спарклайнами (Sparklines):** компактные карточки с микро-трендами (+12.4% MoM) прямо внутри карточки.
- **Динамическая смена палитры под проект:**
  * **Marketplace:** Трендовый тёмный изумруд & золото (E-commerce).
  * **B2B SaaS:** Stripe-стиль (глубокий индиго, фиолетовый градиент).
  * **Fintech & Fraud:** Bloomberg Terminal / Dark Graphite (неоновый зеленый/красный алерт).
  * **Game LiveOps:** Cyber Neon (глубокий космос, неоновый циан и фуксия).
  * **HealthTech:** Clean Clinical (мягкий графит, бирюзовый тил).

---

## 2. Спецификация 5 проектов

```
bi_portfolio_hub/
├── run.bat                          # Запуск всего хаба в 1 клик
├── requirements.txt                 # streamlit, plotly, duckdb, pandas, numpy, pyarrow
├── hub.py                           # Главный навигационный хаб и селектор проектов
├── core/
│   ├── theme.py                     # Движок CSS, палитр и KPI-карточек
│   └── database.py                  # Оптимизированный DuckDB слой
├── data/                            # Parquet-хранилище (все 5 проектов)
│   ├── marketplace_*.parquet
│   ├── saas_*.parquet
│   ├── fintech_*.parquet
│   ├── gaming_*.parquet
│   └── health_*.parquet
└── projects/
    ├── 1_marketplace/               # Модуль Marketplace (переносим и стилизуем)
    ├── 2_saas_metrics/              # Модуль B2B SaaS (MRR/ARR, Churn, Magic Number)
    ├── 3_fintech_fraud/             # Модуль Fintech (Транзакции, Risk Scoring, Аномалии)
    ├── 4_gaming_liveops/            # Модуль Gaming (DAU/MAU, Retention D1/D7/D30, Баланс валюты)
    └── 5_healthtech/                # Модуль HealthTech (Биометрия, Риск-когорты, Пациенты)
```

---

## 3. Токено-эффективный план выполнения

1. **Фаза 1: Инфраструктура и UI-движок (Orchestrator):**
   * Создание `core/theme.py` с готовыми компонентами: `kpi_card()`, `section_header()`, `styled_plotly_chart()`.
   * Создание `hub.py` с витриной проектов на главной странице.
2. **Фаза 2: Генерация компактных данных (Python Script):**
   * Один скрипт генерирует все 5 реалистичных Parquet датасетов (суммарный вес < 5 МБ).
3. **Фаза 3: Сборка 4 новых проектов (Шаблонизированный пайплайн):**
   * Интеграция готового проекта Marketplace.
   * Реализация B2B SaaS (MRR воронка, когорты подписок, Churn).
   * Реализация Fintech Fraud (Матрица риска, таймлайн аномалий, географический фрод).
   * Реализация Game LiveOps (DAU/MAU Stickiness, воронка уровней, экономика).
   * Реализация HealthTech (Биометрические тренды, группы риска, когорты).
4. **Фаза 4: Верификация и One-Click Runner:**
   * Проверка запуска всех 5 проектов через `hub.py`.
   * Создание надежного `run.bat` и `README.md`.
   * Готовность к заливке на Streamlit Cloud одной кнопкой.

---

## 4. Вопрос для согласования:
План оптимизирован под максимальную экономию токенов и премиальный внешний вид. Утверждаем и начинаем сборку?
