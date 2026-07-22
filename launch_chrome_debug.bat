@echo off
echo ===================================================
echo   Shopee Crawler - Launch Chrome Debug Mode (9222)
echo ===================================================
echo.

set "CHROME_PATH="

if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
) else if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=%LocalAppData%\Google\Chrome\Application\chrome.exe"
)

if "%CHROME_PATH%"=="" (
    echo [ERROR] Google Chrome tidak ditemukan di lokasi standar!
    echo Harap jalankan Chrome secara manual dengan perintah:
    echo chrome.exe --remote-debugging-port=9222
    pause
    exit /b 1
)

echo [INFO] Membuka Chrome dari: "%CHROME_PATH%"
echo [INFO] Port Remote Debugging: 9222
echo.
echo Pastikan Anda sudah login ke Shopee di jendela Chrome ini jika diperlukan.
echo.

start "" "%CHROME_PATH%" --remote-debugging-port=9222
echo [OK] Chrome Debugging Mode berhasil dijalankan!
