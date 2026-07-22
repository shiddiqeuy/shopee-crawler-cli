@echo off
setlocal enabledelayedexpansion

set PYTHONIOENCODING=utf-8
chcp 65001 >nul 2>&1

echo ===================================================
echo   Shopee Crawler - Launch Chrome Debugger Mode
echo ===================================================
echo.

set "CHROME_PATH="

if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if "%CHROME_PATH%"=="" if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if "%CHROME_PATH%"=="" if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=%LocalAppData%\Google\Chrome\Application\chrome.exe"

if "%CHROME_PATH%"=="" (
    echo [ERROR] Google Chrome tidak ditemukan di lokasi standar!
    echo Harap jalankan Chrome secara manual dengan perintah:
    echo chrome.exe --remote-debugging-port=9222
    pause
    exit /b 1
)

set "USER_DATA_DIR=%LocalAppData%\Google\Chrome\User Data-Crawler"
if not exist "%USER_DATA_DIR%" mkdir "%USER_DATA_DIR%"

echo [INFO] Executable: "%CHROME_PATH%"
echo [INFO] User Data : "%USER_DATA_DIR%"
echo [INFO] Port      : 9222
echo.
echo Menjalankan Google Chrome Debugger...
echo Sesi login Shopee Anda di Chrome ini akan tersimpan selamanya.
echo.

start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%USER_DATA_DIR%" "https://shopee.co.id"
echo [OK] Chrome Debugger berhasil dibuka di port 9222!
