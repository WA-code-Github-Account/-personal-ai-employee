# WhatsApp Watcher - Setup Guide (D: Drive)

## ✅ Installation Status

| Component | Status | Location |
|-----------|--------|----------|
| Playwright | ✅ Installed | D:\Python_Packages |
| Chromium Browser | ⏳ Downloading | D:\Python_Packages\playwright |
| WhatsApp Watcher Script | ✅ Ready | digital-fte\whatsapp_watcher.py |

---

## 🚀 Quick Setup (Complete in 5 minutes)

### Step 1: Finish Chromium Installation

Chromium browser download ho raha hai. Complete karne ke liye:

```bash
# Open new terminal as Administrator
cd D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte

# Set environment variable
set PYTHONPATH=D:\Python_Packages

# Install Chromium (will take 2-3 minutes)
python -m playwright install chromium
```

**Download Size:** ~173MB  
**Time:** 2-5 minutes (depends on internet speed)

---

### Step 2: Verify Installation

```bash
# Check if Chromium is installed
set PYTHONPATH=D:\Python_Packages
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK!')"
```

**Expected Output:**
```
Playwright OK!
```

---

### Step 3: Run WhatsApp Watcher

```bash
cd D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte
python whatsapp_watcher.py
```

**First Run:**
1. Browser window open hogi
2. WhatsApp Web QR code display hoga
3. Apne phone se QR code scan karein:
   - WhatsApp open karein
   - Settings → Linked Devices → Link a Device
   - QR code scan karein

---

### Step 4: Choose Monitoring Mode

```
Choose mode:
1. Quick Test (5 minutes)
2. Extended Monitoring (30 minutes)
3. Continuous Monitoring (until stopped)
4. Custom Duration

Enter choice (1-4, default=2):
```

**Recommendation:** Start with mode 1 (Quick Test) to verify everything works.

---

## 📂 Output Location

**Urgent messages save honge:**
```
D:\AI_Workspace_bronze_silver_gold_platinum\AI_Employee_Vault\Needs_Action\whatsapp\
```

**Example File:**
```
WhatsApp_20260222_230145_John_Doe.md
```

---

## 🔍 Monitored Keywords

Ye keywords detect honge:

1. urgent
2. asap
3. invoice
4. payment
5. help
6. emergency
7. critical
8. important
9. immediately

**Example:**
```
"Urgent payment pending hai" → DETECTED ✓
"Please help me" → DETECTED ✓
"Normal message" → IGNORED ✗
```

---

## ⚙️ Configuration

### Change Keywords

Edit `whatsapp_watcher.py` line ~57:

```python
URGENT_KEYWORDS = [
    "urgent",
    "asap",
    "invoice",
    "payment",
    "help",
    # Add your own keywords here
    "custom_keyword"
]
```

### Change Check Interval

Edit `whatsapp_watcher.py` line ~69:

```python
CHECK_INTERVAL = 30  # seconds
```

### Change Monitoring Folder

Edit `whatsapp_watcher.py` line ~51:

```python
WHATSAPP_DIR = "D:/Your/Custom/Path/whatsapp"
```

---

## 🎯 Usage Examples

### Quick Test (5 minutes)
```bash
python whatsapp_watcher.py
# Select: 1
# Wait for QR scan
# Done!
```

### Extended Monitoring (30 minutes)
```bash
python whatsapp_watcher.py
# Select: 2
# Background mode: n
```

### Continuous Monitoring (Background)
```bash
python whatsapp_watcher.py
# Select: 3
# Background mode: y
```

### Run as Windows Service (Advanced)

Create `whatsapp_watcher.bat`:
```batch
@echo off
set PYTHONPATH=D:\Python_Packages
cd D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte
python whatsapp_watcher.py
```

**Task Scheduler mein add karein:**
1. Task Scheduler open karein
2. Create Basic Task
3. Name: "WhatsApp Watcher"
4. Trigger: At log on
5. Action: Start a program
6. Program: `whatsapp_watcher.bat`

---

## 📊 Sample Output

**Console Output:**
```
============================================================
WhatsApp Watcher - AI Employee System
============================================================

Monitoring for urgent keywords:
  1. urgent
  2. asap
  3. invoice
  4. payment
  5. help
  6. emergency
  7. critical
  8. important
  9. immediately

Choose mode:
1. Quick Test (5 minutes)
2. Extended Monitoring (30 minutes)
3. Continuous Monitoring (until stopped)
4. Custom Duration

Enter choice (1-4, default=2): 1

------------------------------------------------------------
Starting WhatsApp Watcher...
QR code scan karein agar display ho
------------------------------------------------------------

============================================================
WhatsApp Message Monitoring Started
============================================================
Checking every 30 seconds
Keywords: urgent, asap, invoice, payment, help, emergency, critical, important, immediately
Duration: 300 seconds

[INFO] Keywords matched: urgent, payment
[INFO] URGENT message detected from John Doe
[INFO] Urgent message saved: WhatsApp_20260222_230145_John_Doe.md
  Sender: John Doe
  Keywords: urgent, payment
  Path: D:\...\Needs_Action\whatsapp\WhatsApp_20260222_230145_John_Doe.md

============================================================
Monitoring Summary
============================================================
Total checks: 10
Urgent messages found: 1
Folder: D:\...\Needs_Action\whatsapp
```

---

## 📁 Sample Saved Message

**File:** `WhatsApp_20260222_230145_John_Doe.md`

```markdown
---
type: whatsapp_message
priority: urgent
keywords: urgent, payment
sender: John Doe
received_at: 2026-02-22T23:01:45
status: new
---

# WhatsApp Urgent Message

## Sender Information
- **Name:** John Doe
- **Received:** 2026-02-22T23:01:45
- **Platform:** WhatsApp Web

## Message Content
Hi, urgent payment pending hai. Please check invoice #12345.

## Detected Keywords
- urgent
- payment

## Action Required
<!-- Yahan action likhen ke is message ka kya karna hai -->

## Response
<!-- Yahan response draft likhen -->

---
*Generated by AI Employee WhatsApp Watcher*
```

---

## 🔧 Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'playwright'"

**Solution:**
```bash
set PYTHONPATH=D:\Python_Packages
python -c "import playwright; print('OK')"
```

### Issue 2: "Chromium not found"

**Solution:**
```bash
set PYTHONPATH=D:\Python_Packages
python -m playwright install chromium
```

### Issue 3: QR Code nahi display ho raha

**Solution:**
- Headless mode off karein (jab pucha jaye "n" select karein)
- Browser window manually check karein
- Internet connection verify karein

### Issue 4: Messages detect nahi ho rahe

**Solution:**
- WhatsApp Web properly load hone dein
- Koi unread message aane dein test ke liye
- Console logs check karein

### Issue 5: "No space left on device"

**Solution:**
```bash
# Clear pip cache
pip cache purge

# Clear temp files
del /q %TEMP%\*
```

---

## 📝 Environment Variables (Optional)

Create `.env` file:

```env
# WhatsApp Watcher Configuration
WHATSAPP_CHECK_INTERVAL=30
WHATSAPP_KEYWORDS=urgent,asap,invoice,payment,help
WHATSAPP_MONITORING_DURATION=1800
WHATSAPP_HEADLESS=false
```

---

## 🎯 Next Steps

1. ✅ **Complete Chromium Installation**
   ```bash
   set PYTHONPATH=D:\Python_Packages
   python -m playwright install chromium
   ```

2. ✅ **Test WhatsApp Watcher**
   ```bash
   python whatsapp_watcher.py
   ```

3. ✅ **Check Output Folder**
   ```
   D:\AI_Workspace_bronze_silver_gold_platinum\AI_Employee_Vault\Needs_Action\whatsapp\
   ```

4. ✅ **Setup Auto-Start** (Optional)
   - Task Scheduler mein add karein
   - Ya manually run karein jab needed ho

---

## 📞 Support

**Log File:** `whatsapp_watcher.log`  
**Documentation:** `whatsapp_watcher.py` (lines 1-77)  
**Source Code:** `D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte\whatsapp_watcher.py`

---

*Generated for AI Employee System - Platinum Tier*  
*WhatsApp Watcher v1.0*
