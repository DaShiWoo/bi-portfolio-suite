@echo off
setlocal
chcp 65001 >nul
title Executive BI Analytics Suite Launcher
cd /d "%~dp0"

echo ==============================================================================
echo   EXECUTIVE BI PORTFOLIO SUITE - 1-CLICK LAUNCHER (5 VERTICALS)
echo ==============================================================================
echo.

:: 1. Detect Python from local venv or sibling venv
if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
    goto :CHECK_DEPS
)
if exist "..\marketplace_bi\.venv\Scripts\python.exe" (
    set "PY=..\marketplace_bi\.venv\Scripts\python.exe"
    goto :CHECK_DEPS
)

:: Search system Python
where py.exe >nul 2>&1
if %ERRORLEVEL% equ 0 (
    py -3 -m venv .venv
    set "PY=.venv\Scripts\python.exe"
    goto :INSTALL_DEPS
)
where python.exe >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python -m venv .venv
    set "PY=.venv\Scripts\python.exe"
    goto :INSTALL_DEPS
)

echo [ERROR] Python 3.10+ was not found on your system!
echo Please install Python and check "Add to PATH".
goto :ERROR_EXIT

:INSTALL_DEPS
echo [SETUP] Installing dependencies into .venv...
"%PY%" -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 goto :ERROR_EXIT

:CHECK_DEPS
echo [1/2] Checking synthetic multi-industry datasets...
if not exist "data\marketplace_orders.parquet" goto :GEN_DATA
if not exist "data\saas_subscriptions.parquet" goto :GEN_DATA
if not exist "data\fintech_transactions.parquet" goto :GEN_DATA
if not exist "data\gaming_telemetry.parquet" goto :GEN_DATA
if not exist "data\health_telemetry.parquet" goto :GEN_DATA
echo [OK] All 5 Parquet datasets verified in data\
goto :LAUNCH

:GEN_DATA
echo [DATA] Generating 5 domain datasets...
"%PY%" generate_all_data.py
if %ERRORLEVEL% neq 0 goto :ERROR_EXIT
echo [OK] Datasets ready.

:LAUNCH
echo.
echo ==============================================================================
echo [2/2] Launching BI Portfolio Suite at http://localhost:8501 ...
echo The browser will open automatically.
echo (Press Ctrl+C in this terminal window to stop the server)
echo ==============================================================================
echo.

"%PY%" -m streamlit run hub.py --server.headless=false --browser.serverAddress=localhost

if %ERRORLEVEL% neq 0 goto :ERROR_EXIT
goto :END

:ERROR_EXIT
echo.
echo [FAILED] An error occurred. Press any key to exit.
pause
exit /b 1

:END
pause
