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

set "USER_DATA_DIR=%LocalAppData%\Google\Chrome\User Data"
set "PROFILE_NAME=Default"

if not "%~1"=="" (
    set "PROFILE_NAME=%~1"
    goto :LAUNCH
)

echo [INFO] Mendeteksi profil Google Chrome yang tersedia...
echo.
set /a count=0

if exist "%USER_DATA_DIR%\Default" (
    set /a count+=1
    set "prof_!count!=Default"
    echo  !count!. Default (Profil Utama)
)

for /d %%D in ("%USER_DATA_DIR%\Profile *") do (
    set "folder=%%~nxD"
    set /a count+=1
    set "prof_!count!=!folder!"
    echo  !count!. !folder!
)

if !count! gtr 0 (
    echo.
    set /p choice="Pilih nomor profil Chrome (1-!count!) [default 1]: "
    if not "!choice!"=="" (
        if defined prof_!choice! (
            set "PROFILE_NAME=!prof_!choice!!"
        )
    )
)

:LAUNCH
echo.
echo [INFO] Executable: "%CHROME_PATH%"
echo [INFO] User Data : "%USER_DATA_DIR%"
echo [INFO] Profil    : "%PROFILE_NAME%"
echo [INFO] Port      : 9222
echo.
echo Catatan: Jika Chrome sudah terbuka sebelumnya tanpa port 9222,
echo pastikan untuk menutup Chrome terlebih dahulu agar port 9222 bisa aktif.
echo.

start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%USER_DATA_DIR%" --profile-directory="%PROFILE_NAME%"
echo [OK] Chrome berhasil dibuka dengan profil %PROFILE_NAME% di port 9222!
