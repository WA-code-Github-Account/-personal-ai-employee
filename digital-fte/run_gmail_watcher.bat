@echo off
echo ============================================================
echo Gmail Watcher - AI Employee System
echo ============================================================
echo.
echo Target Account: wahishaikh545@gmail.com
echo Monitoring Folder: AI_Employee_Vault/Inbox/
echo ============================================================
echo.

cd /d "%~dp0"
python gmail_watcher.py

echo.
echo ============================================================
echo Gmail Watcher Stopped
echo ============================================================
