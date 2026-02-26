@echo off
echo ============================================================
echo WhatsApp Watcher - AI Employee System
echo ============================================================
echo.
echo Monitoring WhatsApp Web for urgent messages
echo Keywords: urgent, asap, invoice, payment, help, etc.
echo ============================================================
echo.

cd /d "%~dp0"

REM Set environment variables for D: drive installation
set PYTHONPATH=D:\Python_Packages
set PLAYWRIGHT_BROWSERS_PATH=D:\Playwright_Browsers
set TMP=D:\Temp
set TEMP=D:\Temp

python whatsapp_watcher.py

echo.
echo ============================================================
echo WhatsApp Watcher Stopped
echo ============================================================
