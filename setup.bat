@echo off
setlocal enabledelayedexpansion

set PYTHONIOENCODING=utf-8
chcp 65001 >nul 2>&1

echo ===================================================

echo   Shopee Market Research CLI - Setup Initializer
echo ===================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan! Harap install Python 3.13+ dan tambahkan ke PATH.
    pause
    exit /b 1
)

:: 2. Create Virtual Environment if not present
if not exist ".venv" (
    echo [INFO] Membuat Python Virtual Environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Gagal membuat virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual Environment berhasil dibuat.
) else (
    echo [INFO] Virtual Environment (.venv) sudah ada.
)

:: 3. Activate Virtual Environment
call .venv\Scripts\activate.bat

:: 4. Install Dependencies
echo.
echo [INFO] Menginstall dependency project...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -e .
if %errorlevel% neq 0 (
    echo [ERROR] Gagal menginstall dependencies!
    pause
    exit /b 1
)

:: 5. Install Playwright Browsers
echo.
echo [INFO] Menginstall Playwright Chromium Browser...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo [WARNING] Playwright browser install mengalami masalah. Anda mungkin perlu menjalankan 'python -m playwright install chromium' secara manual.
)

:: 6. Copy .env.example if .env missing
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] File .env berhasil dibuat dari .env.example
    )
)

echo.
echo ===================================================
echo   SETUP SELESAI! Sektor siap digunakan.
echo ===================================================
echo   Jalankan CLI dengan:
echo     - Menu Interaktif: run.bat menu   (atau python run.py)
echo     - Langsung Perintah: run.bat search "kopi"
echo     - Jalankan Chrome Debug: launch_chrome_debug.bat
echo ===================================================
echo.
pause
