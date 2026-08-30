@echo off
setlocal
chcp 65001 >nul
title GitHub Auto-Push - BI Portfolio Suite
cd /d "%~dp0"

echo ==============================================================================
echo   GITHUB 1-CLICK PUSH - BI PORTFOLIO SUITE
echo ==============================================================================
echo.

set "DEFAULT_URL=https://github.com/DaShiWoo/bi-portfolio-suite.git"

echo Ваш GitHub аккаунт: DaShiWoo
echo.
echo Если репозиторий "bi-portfolio-suite" уже создан на github.com/new,
echo просто нажмите ENTER. 
echo Либо вставьте другую ссылку на репозиторий:
echo.
set /p REPO_URL="URL репозитория [%DEFAULT_URL%]: "

if "%REPO_URL%"=="" set "REPO_URL=%DEFAULT_URL%"

echo.
echo [1/3] Настройка remote origin -> %REPO_URL%...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
git branch -M master

echo [2/3] Отправка коммита на GitHub...
echo (Если появится окно авторизации GitHub - подтвердите вход в браузере)
echo.

git push -u origin master

if %ERRORLEVEL% equ 0 (
    echo.
    echo ==============================================================================
    echo [УСПЕХ] Проект успешно отправлен на GitHub!
    echo.
    echo Теперь перейдите на: https://share.streamlit.io
    echo Выберите ваш репозиторий и укажите файл: hub.py
    echo ==============================================================================
) else (
    echo.
    echo [ОШИБКА] Не удалось отправить код. Убедитесь, что репозиторий создан на github.com/new.
)

echo.
pause
