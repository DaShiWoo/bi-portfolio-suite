@echo off
setlocal enabledelayedexpansion

title Support Ops P&L Analytics - Executive Demo (Port 8502)

echo =====================================================================
echo  EverHelp / C-Level Analytics: Support Ops P&L Intelligence
echo  Zendesk Tickets -^> DuckDB OLAP Cohorts -^> P&L Unit Margin
echo =====================================================================
echo.

cd /d "%~dp0"

:: 1. Locate Python executable in workspace root .venv
set "PYTHON_EXE=..\..\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

:: 2. Check if datasets exist; generate if missing
if not exist "data\subscriptions_cohorts.parquet" (
    echo [INFO] Synthetic datasets not found. Generating Parquet tables...
    "%PYTHON_EXE%" generate_support_data.py
    if errorlevel 1 (
        echo [ERROR] Data generation failed! Check environment.
        pause
        exit /b 1
    )
) else (
    echo [OK] Parquet datasets detected in data\
)

echo.
echo [INFO] Launching Executive Streamlit Dashboard on http://localhost:8502 ...
echo Press Ctrl+C in this terminal to stop the server.
echo.

"%PYTHON_EXE%" -m streamlit run app.py --server.port 8502 --server.headless false

pause
