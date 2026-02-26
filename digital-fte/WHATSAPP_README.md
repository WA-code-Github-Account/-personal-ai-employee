# 🚀 WhatsApp Watcher - Complete Installation Guide

**Last Updated:** 2026-02-22  
**Status:** Ready to Install

---

## 📋 Table of Contents

1. [Quick Start (Recommended)](#quick-start-recommended)
2. [Manual Installation](#manual-installation)
3. [Troubleshooting](#troubleshooting)
4. [Usage Guide](#usage-guide)
5. [FAQ](#faq)

---

## ⚡ Quick Start (Recommended)

### Step 1: Run Quick Start Script

**Double-click this file:**
```
D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte\whatsapp_quick_start.bat
```

**OR run from terminal:**
```bash
cd D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte
whatsapp_quick_start.bat
```

### Step 2: Wait for Installation

Script automatically:
1. ✅ Checks if Chromium is installed
2. ✅ Downloads Chromium if needed (~173MB, 5-10 min)
3. ✅ Verifies installation
4. ✅ Starts WhatsApp Watcher

### Step 3: Scan QR Code

When browser opens:
1. WhatsApp Web QR code will appear
2. Open WhatsApp on your phone
3. Settings → Linked Devices → Link a Device
4. Scan QR code

### Step 4: Choose Monitoring Mode

```
Choose mode:
1. Quick Test (5 minutes)     ← Recommended for first time
2. Extended Monitoring (30 minutes)
3. Continuous Monitoring
4. Custom Duration
```

**Done!** Urgent messages will be saved automatically.

---

## 🔧 Manual Installation

### Prerequisites

- Windows 10/11
- Python 3.10+
- 200MB free disk space (D: drive)
- Internet connection

### Step 1: Set Environment Variables

```bash
set PLAYWRIGHT_BROWSERS_PATH=D:\Playwright_Browsers
set PYTHONPATH=D:\Python_Packages
```

### Step 2: Install Playwright (Already Done ✅)

```bash
pip install playwright --target D:\Python_Packages
```

**Status:** ✅ Already installed

### Step 3: Install Chromium

```bash
set PLAYWRIGHT_BROWSERS_PATH=D:\Playwright_Browsers
set PYTHONPATH=D:\Python_Packages
python -m playwright install chromium
```

**Download Size:** ~173MB  
**Time:** 5-10 minutes

### Step 4: Verify Installation

```bash
set PLAYWRIGHT_BROWSERS_PATH=D:\Playwright_Browsers
set PYTHONPATH=D:\Python_Packages

python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(); print('Chromium OK!'); b.close(); p.stop()"
```

**Expected Output:**
```
Chromium OK!
```

### Step 5: Run WhatsApp Watcher

```bash
cd D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte
python whatsapp_watcher.py
```

---

## 🔍 Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'playwright'"

**Solution:**
```bash
set PYTHONPATH=D:\Python_Packages
python -c "import playwright; print('OK')"
```

If error persists:
```bash
pip install playwright --target D:\Python_Packages
```

---

### Issue 2: "Executable doesn't exist"

**Solution:**
```bash
set PLAYWRIGHT_BROWSERS_PATH=D:\Playwright_Browsers
python -m playwright install chromium --force
```

---

### Issue 3: Download timeout

**Cause:** Slow internet or Google CDN issue

**Solutions:**

**Option A: Retry**
```bash
set PLAYWRIGHT_BROWSERS_PATH=D:\Playwright_Browsers
python -m playwright install chromium
```

**Option B: Use Microsoft CDN**
```bash
set PLAYWRIGHT_BROWSERS_PATH=D:\Playwright_Browsers
set PLAYWRIGHT_DOWNLOAD_HOST=playwright.download.prss.microsoft.com
python -m playwright install chromium
```

**Option C: Manual Download**
1. Download from: https://googlechromelabs.github.io/chrome-for-testing/
2. Extract to: `D:\Playwright_Browsers\chromium-1208\`
3. Run verification

---

### Issue 4: QR Code nahi display ho raha

**Solutions:**
1. Headless mode off karein (jab pucha jaye "n" select karein)
2. Browser window manually check karein
3. Internet connection verify karein
4. WhatsApp Web pe manually login karke dekhein

---

### Issue 5: Messages detect nahi ho rahe

**Solutions:**
1. WhatsApp Web properly load hone dein (wait 30 seconds)
2. Koi test message bhejein with keyword "urgent"
3. Console logs check karein
4. Keywords list verify karein

---

## 📖 Usage Guide

### Basic Commands

```bash
# Quick test (5 minutes)
python whatsapp_watcher.py
# Select: 1

# Extended monitoring (30 minutes)
python whatsapp_watcher.py
# Select: 2

# Continuous monitoring
python whatsapp_watcher.py
# Select: 3

# Background mode (no window)
python whatsapp_watcher.py
# When asked: y
```

### Output Location

**Messages save honge:**
```
D:\AI_Workspace_bronze_silver_gold_platinum\AI_Employee_Vault\Needs_Action\whatsapp\
```

**Log file:**
```
D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte\whatsapp_watcher.log
```

### Detected Keywords

```
urgent, asap, invoice, payment, help, 
emergency, critical, important, immediately
```

### Custom Keywords

Edit `whatsapp_watcher.py` line ~57:

```python
URGENT_KEYWORDS = [
    "urgent",
    "asap",
    "invoice",
    "payment",
    "help",
    # Add your own:
    "custom_keyword",
    "another_keyword"
]
```

---

## ❓ FAQ

### Q: Kitna time take karta hai installation?
**A:** 5-10 minutes (Chromium download pe depend karta hai)

### Q: Kya har baar QR code scan karna parega?
**A:** Session save rehta hai, next time auto-login ho sakta hai

### Q: Kya WhatsApp Web open rehna zaroori hai?
**A:** Haan, browser window open rehni chahiye monitoring ke dauran

### Q: Internet speed kam hai toh?
**A:** Raat ke time try karein jab network fast hota hai

### Q: Multiple WhatsApp accounts?
**A:** Haan, multiple instances run kar sakte hain different terminals mein

### Q: Backup kaise lein?
**A:** `Needs_Action/whatsapp/` folder ka backup le lein

### Q: Can I run it as a service?
**A:** Haan, Task Scheduler mein add kar sakte hain

---

## 🎯 Quick Reference

### Environment Setup
```bash
set PLAYWRIGHT_BROWSERS_PATH=D:\Playwright_Browsers
set PYTHONPATH=D:\Python_Packages
```

### Install Chromium
```bash
python -m playwright install chromium
```

### Run Watcher
```bash
python whatsapp_watcher.py
```

### Check Output
```bash
dir D:\AI_Workspace_bronze_silver_gold_platinum\AI_Employee_Vault\Needs_Action\whatsapp\
```

---

## 📞 Support Files

| File | Purpose |
|------|---------|
| `whatsapp_watcher.py` | Main script |
| `whatsapp_quick_start.bat` | One-click installer |
| `WHATSAPP_SETUP.md` | Detailed setup guide |
| `CHROMIUM_STATUS.md` | Installation troubleshooting |
| `FINAL_STATUS_WHATSAPP.md` | Current status report |
| `README.md` | This file |

---

## ✅ Installation Checklist

- [ ] Playwright installed (✅ Already done)
- [ ] Chromium downloaded (⏳ In progress)
- [ ] Verification successful
- [ ] QR code scanned
- [ ] First message detected
- [ ] Message saved to vault

---

**Ready to start?** Run `whatsapp_quick_start.bat`! 🚀

---

*Generated for AI Employee System - Platinum Tier*  
*WhatsApp Watcher v1.0*
