@echo off
REM WhatsApp Watcher - Quick Start Script
REM D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte\whatsapp_quick_start.bat

echo ============================================================
echo WhatsApp Watcher - Quick Start
echo ============================================================
echo.

REM Set environment variables
set PLAYWRIGHT_BROWSERS_PATH=D:\Playwright_Browsers
set PYTHONPATH=D:\Python_Packages

echo [1/3] Checking Chromium installation...
if exist "D:\Playwright_Browsers\chromium-*" (
    echo [OK] Chromium found!
    goto :verify
) else (
    echo [WAIT] Chromium not found. Installing...
    goto :install
)

:install
echo.
echo Downloading Chromium (~173MB)...
echo This may take 5-10 minutes depending on internet speed
echo.
python -m playwright install chromium
if errorlevel 1 (
    echo [ERROR] Installation failed. Please check internet connection.
    pause
    exit /b 1
)

:verify
echo.
echo [2/3] Verifying installation...
python -c "from playwright.sync_api import sync_playwright; print('[OK] Playwright verified!')"
if errorlevel 1 (
    echo [ERROR] Verification failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Starting WhatsApp Watcher...
echo.
echo ============================================================
echo IMPORTANT: QR Code Scan Instructions
echo ============================================================
echo 1. Browser window will open
echo 2. WhatsApp Web QR code will appear
echo 3. Open WhatsApp on your phone
echo 4. Go to: Settings -^> Linked Devices -^> Link a Device
echo 5. Scan the QR code
echo ============================================================
echo.
pause

REM Run WhatsApp Watcher
cd /d "%~dp0"
python whatsapp_watcher.py

echo.
echo ============================================================
echo WhatsApp Watcher Complete
echo ============================================================
echo Check folder: D:\AI_Workspace_bronze_silver_gold_platinum\AI_Employee_Vault\Needs_Action\whatsapp\
echo Log file: whatsapp_watcher.log
echo ============================================================
pause
