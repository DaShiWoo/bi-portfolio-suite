# Teamwork Project Prompt — Enterprise BI Portfolio Hub

> Status: Launched
> Goal: Enterprise-grade architectural refactoring, DRY filters, caching, design audit, and automated test suite
> Requested team: Full team (Core Architect, Domain Refactorers, Design Auditor, QA Automation)

Enterprise BI Portfolio Hub refactoring to Senior/Staff BI Architect standards: DRY architecture, cached data layer, comprehensive design review (WCAG AA), and automated test framework.

Working directory: C:\Users\danja\.gemini\antigravity\scratch\bi_portfolio_hub
Integrity mode: development

## Requirements

### R1. Core Architecture & Performance Foundation
- Implement centralized cached data loader in `core/data_loader.py` with `@st.cache_data` and schema validation.
- Implement declarative filter engine `core/filters.py` handling sidebar controls, active filter badges, and graceful empty-state handling.
- Enhance theme engine `core/theme.py` with cross-browser gradient fallbacks and WCAG AA contrast adjustments.

### R2. Domain Pages Standardization (25 Pages)
- Refactor all 25 pages across Marketplace, SaaS, Fintech, Gaming, and HealthTech to use `core/filters.py` and `core/data_loader.py`.
- Type-annotate all page `render(df: pd.DataFrame) -> None` functions with proper docstrings.
- Ensure graceful rendering when filters yield 0 rows (no crashes or division by zero).

### R3. Visual & UX Design Audit
- Perform a thorough design audit of all 5 themes (Marketplace, SaaS, Fintech, Gaming, HealthTech).
- Verify typography hierarchy, spacing rhythm, chart palette harmony, and contrast.
- Generate `DESIGN_AUDIT_REPORT.md` documenting findings, WCAG compliance, and applied improvements.

### R4. Automated Testing Framework
- Implement a complete `pytest` test suite in `tests/`:
  - `tests/test_data_loader.py` (parquet loading, schema integrity)
  - `tests/test_filters.py` (filtering logic, edge cases, empty states)
  - `tests/test_pages_smoke.py` (smoke tests for all 25 page renderers)
- Verify 100% test pass rate with `pytest -v`.

### R5. Deployment & Release
- Verify full syntax compilation (`py_compile`).
- Commit and push to GitHub repository with clean release message.

## Acceptance Criteria

### Test & Build Criteria
- [ ] `pytest` passes with 0 failures across all tests.
- [ ] `py_compile` succeeds on 100% of Python files.
- [ ] All 25 pages render without unhandled exceptions on empty or filtered datasets.
- [ ] Parquet datasets loaded via `@st.cache_data`.
- [ ] `DESIGN_AUDIT_REPORT.md` created in repository root.
- [ ] Clean push to GitHub master branch.
