@echo off
setlocal

set PYTHONIOENCODING=utf-8
chcp 65001 >nul 2>&1

:: Check if virtual environment exists and activate
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

:: If no arguments provided, open interactive menu
if "%~1"=="" (
    python run.py menu
) else (
    python run.py %*
)

