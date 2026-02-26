#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher - Urgent Message Monitor
WhatsApp Web par urgent messages ko monitor karne wala module

═══════════════════════════════════════════════════════════════════════════════
📱 SETUP INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════

Step 1: Install Playwright
─────────────────────────────────────────
pip install playwright
playwright install chromium

Step 2: Run WhatsApp Watcher
─────────────────────────────────────────
python whatsapp_watcher.py

Step 3: Scan QR Code
─────────────────────────────────────────
- WhatsApp Web QR code scan karein apne phone se
- Session save ho jayega, next time auto-login hoga

Step 4: Monitoring Start
─────────────────────────────────────────
- Watcher har 30 seconds mein check karta hai
- Urgent keywords detect hone par file save hoti hai
- Folder: Needs_Action/whatsapp/

═══════════════════════════════════════════════════════════════════════════════
⚠️ IMPORTANT NOTES
═══════════════════════════════════════════════════════════════════════════════

• WhatsApp Web session open rehna chahiye
• Phone internet se connected hona chahiye
• QR code scan karna parega har session mein
• Messages sirf unread/unseen hi detect honge

═══════════════════════════════════════════════════════════════════════════════
🔗 USEFUL LINKS
═══════════════════════════════════════════════════════════════════════════════

• Playwright Docs: https://playwright.dev/python/
• WhatsApp Web: https://web.whatsapp.com

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Roman Urdu: Playwright imports
try:
    from playwright.sync_api import sync_playwright, Page, Browser
except ImportError:
    print("ERROR: Playwright not installed!")
    print("Install karein: pip install playwright")
    print("Phir run karein: playwright install chromium")
    sys.exit(1)

# Roman Urdu: Audit logger aur error recovery ko import karna
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_logger import log_task_start, log_task_complete, log_file_operation, log_error
from error_recovery import retry_with_backoff, safe_execute

# Roman Urdu: Environment variables load karna
load_dotenv()

# Roman Urdu: Configuration aur global variables
VAULT_BASE = "D:/AI_Workspace_bronze_silver_gold_platinum/AI_Employee_Vault"
WHATSAPP_DIR = os.path.join(VAULT_BASE, "Needs_Action", "whatsapp")

# Roman Urdu: WhatsApp Web URL
WHATSAPP_WEB_URL = "https://web.whatsapp.com"

# Roman Urdu: Urgent keywords list (case-insensitive)
URGENT_KEYWORDS = [
    "urgent",
    "asap",
    "invoice",
    "payment",
    "help",
    "emergency",
    "critical",
    "important",
    "immediately"
]

# Roman Urdu: Monitoring interval (seconds)
CHECK_INTERVAL = 30

# Roman Urdu: Logging setup
LOG_FILE = "whatsapp_watcher.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WhatsAppWatcher:
    """
    WhatsApp Web Message Monitor
    WhatsApp Web par messages ko monitor karne wala class
    """

    def __init__(self, headless: bool = False):
        """
        Initialize WhatsApp Watcher
        WhatsApp Watcher ko initialize karna

        Args:
            headless: If True, browser without UI chalega
        """
        # Roman Urdu: Configuration set karna
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.processed_messages = set()  # Roman Urdu: Duplicate messages avoid karne ke liye

        # Roman Urdu: WhatsApp directory ensure karna
        os.makedirs(WHATSAPP_DIR, exist_ok=True)

        # Roman Urdu: Initialization log
        logger.info(f"WhatsApp Watcher initialized (headless={headless})")
        logger.info(f"Monitoring folder: {WHATSAPP_DIR}")
        logger.info(f"Keywords: {', '.join(URGENT_KEYWORDS)}")

        # Roman Urdu: Audit log
        log_task_start("WhatsApp Watcher Init", source="whatsapp_watcher",
                      headless=str(headless))

    def start_browser(self):
        """
        Start Playwright browser and open WhatsApp Web
        Playwright browser start karna aur WhatsApp Web kholna
        """
        # Roman Urdu: Browser start karne ka log
        logger.info("Starting browser...")
        log_task_start("Browser Start", source="whatsapp_watcher")

        try:
            # Roman Urdu: Playwright start karna
            self.playwright = sync_playwright().start()

            # Roman Urdu: Browser launch karna
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )

            # Roman Urdu: Context create karna (persistent storage ke saath)
            context = self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            # Roman Urdu: Page create karna
            self.page = context.new_page()

            # Roman Urdu: WhatsApp Web navigate karna
            logger.info(f"Navigating to {WHATSAPP_WEB_URL}")
            self.page.goto(WHATSAPP_WEB_URL, timeout=60000)

            # Roman Urdu: Success log
            logger.info("Browser started successfully")
            log_task_complete("Browser Start", result="SUCCESS",
                             source="whatsapp_watcher")

        except Exception as e:
            error_msg = f"Browser start error: {str(e)}"
            logger.error(error_msg)
            log_error("BROWSER_START_ERROR", str(e),
                     action="start_browser", source="whatsapp_watcher")
            raise

    def wait_for_whatsapp_load(self, timeout: int = 120):
        """
        Wait for WhatsApp Web to fully load
        WhatsApp Web ke fully load hone ka wait karna

        Args:
            timeout: Maximum wait time in seconds
        """
        # Roman Urdu: Wait ka log
        logger.info(f"Waiting for WhatsApp Web to load (timeout: {timeout}s)...")
        logger.info("QR code scan karein agar display ho raha hai")

        try:
            # Roman Urdu: QR code ya chat list ka wait karna
            # WhatsApp Web loaded hai jab chat list visible ho
            self.page.wait_for_selector('div[role="navigation"]', timeout=timeout * 1000)

            # Roman Urdu: Success log
            logger.info("WhatsApp Web loaded successfully")
            logger.info("Monitoring shuru ho raha hai...")

        except Exception as e:
            error_msg = f"WhatsApp load timeout: {str(e)}"
            logger.error(error_msg)
            logger.info("QR code scan karna na bhulein!")
            log_error("WHATSAPP_LOAD_ERROR", str(e),
                     action="wait_for_whatsapp_load", source="whatsapp_watcher")
            raise

    def extract_messages(self) -> List[Dict]:
        """
        Extract recent messages from WhatsApp Web
        WhatsApp Web se recent messages extract karna

        Returns:
            list: List of message dictionaries
        """
        # Roman Urdu: Messages extract karne ka log
        logger.debug("Extracting messages from WhatsApp Web...")

        try:
            # Roman Urdu: JavaScript se messages scrape karna
            messages = self.page.evaluate('''() => {
                const messages = [];
                
                // Roman Urdu: Chat list selectors try karna
                const chatSelectors = [
                    'div[role="row"]',
                    'div[data-testid="chat-item"]',
                    'div._3BqNZ'  // Old selector
                ];
                
                let chatElement = null;
                for (const selector of chatSelectors) {
                    chatElement = document.querySelector(selector);
                    if (chatElement) break;
                }
                
                if (!chatElement) {
                    return messages;
                }
                
                // Roman Urdu: Chat title/message extract karna
                const titleElement = chatElement.querySelector('span[title]');
                const messageElement = chatElement.querySelector('span[dir="auto"]');
                const timeElement = chatElement.querySelector('span[dir="auto"]');
                
                if (titleElement && messageElement) {
                    messages.push({
                        sender: titleElement.getAttribute('title') || 'Unknown',
                        message: messageElement.textContent || '',
                        timestamp: new Date().toISOString(),
                        isUnread: chatElement.getAttribute('aria-label')?.includes('unread') || false
                    });
                }
                
                return messages;
            }''')

            # Roman Urdu: Debug log
            logger.debug(f"Extracted {len(messages)} messages")
            return messages

        except Exception as e:
            error_msg = f"Message extraction error: {str(e)}"
            logger.error(error_msg)
            log_error("MESSAGE_EXTRACT_ERROR", str(e),
                     action="extract_messages", source="whatsapp_watcher")
            return []

    def check_keywords(self, message_text: str) -> List[str]:
        """
        Check if message contains urgent keywords
        Check karna ke message mein urgent keywords hain ya nahi

        Args:
            message_text: Message text to check

        Returns:
            list: List of matched keywords
        """
        # Roman Urdu: Text ko lowercase mein convert karna
        message_lower = message_text.lower()

        # Roman Urdu: Keywords match karna
        matched_keywords = []
        for keyword in URGENT_KEYWORDS:
            if keyword.lower() in message_lower:
                matched_keywords.append(keyword)

        # Roman Urdu: Matched keywords log karna
        if matched_keywords:
            logger.info(f"Keywords matched: {', '.join(matched_keywords)}")

        return matched_keywords

    def save_urgent_message(self, sender: str, message: str,
                           keywords: List[str], timestamp: str = None):
        """
        Save urgent message to vault
        Urgent message ko vault mein save karna

        Args:
            sender: Message sender name
            message: Message content
            keywords: Matched urgent keywords
            timestamp: Message timestamp
        """
        # Roman Urdu: Timestamp generate karna
        if not timestamp:
            timestamp = datetime.now().isoformat()

        # Roman Urdu: Unique filename create karna
        timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
        sender_slug = sender.replace(" ", "_").replace("/", "_")[:30]
        filename = f"WhatsApp_{timestamp_file}_{sender_slug}.md"
        filepath = os.path.join(WHATSAPP_DIR, filename)

        # Roman Urdu: Markdown content create karna
        content = f"""---
type: whatsapp_message
priority: urgent
keywords: {', '.join(keywords)}
sender: {sender}
received_at: {timestamp}
status: new
---

# WhatsApp Urgent Message

## Sender Information
- **Name:** {sender}
- **Received:** {timestamp}
- **Platform:** WhatsApp Web

## Message Content
{message}

## Detected Keywords
{chr(10).join(f'- {keyword}' for keyword in keywords)}

## Action Required
<!-- Yahan action likhen ke is message ka kya karna hai -->

## Response
<!-- Yahan response draft likhen -->

---
*Generated by AI Employee WhatsApp Watcher*
"""

        # Roman Urdu: File save karna
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            # Roman Urdu: Audit log
            log_file_operation("WRITE", filepath, result="SUCCESS",
                              file_size=len(content), source="whatsapp_watcher")

            # Roman Urdu: Success log
            logger.info(f"Urgent message saved: {filename}")
            logger.info(f"  Sender: {sender}")
            logger.info(f"  Keywords: {', '.join(keywords)}")
            logger.info(f"  Path: {filepath}")

            return filepath

        except Exception as e:
            error_msg = f"File save error: {str(e)}"
            logger.error(error_msg)
            log_error("FILE_SAVE_ERROR", str(e),
                     file_involved=filepath, action="save_urgent_message")
            return None

    def monitor_messages(self, duration: int = None):
        """
        Monitor WhatsApp messages continuously
        WhatsApp messages ko continuously monitor karna

        Args:
            duration: Monitoring duration in seconds (None = infinite)
        """
        # Roman Urdu: Monitoring start ka log
        logger.info("=" * 60)
        logger.info("WhatsApp Message Monitoring Started")
        logger.info("=" * 60)
        logger.info(f"Checking every {CHECK_INTERVAL} seconds")
        logger.info(f"Keywords: {', '.join(URGENT_KEYWORDS)}")

        if duration:
            logger.info(f"Duration: {duration} seconds")
        else:
            logger.info("Duration: Infinite (Ctrl+C to stop)")

        # Roman Urdu: Audit log
        log_task_start("WhatsApp Monitoring", source="whatsapp_watcher",
                      duration=str(duration) if duration else "infinite")

        start_time = time.time()
        check_count = 0
        messages_found = 0

        try:
            while True:
                # Roman Urdu: Duration check karna
                if duration and (time.time() - start_time) > duration:
                    logger.info(f"Monitoring duration completed: {duration}s")
                    break

                # Roman Urdu: Messages extract karna
                messages = self.extract_messages()

                # Roman Urdu: Har message ko check karna
                for msg in messages:
                    sender = msg.get('sender', 'Unknown')
                    message_text = msg.get('message', '')
                    is_unread = msg.get('isUnread', False)

                    # Roman Urdu: Unique message check (duplicate avoid)
                    message_id = f"{sender}:{message_text[:50]}"
                    if message_id in self.processed_messages:
                        continue

                    # Roman Urdu: Keywords check karna
                    keywords = self.check_keywords(message_text)

                    # Roman Urdu: Agar keywords mile aur message unread hai
                    if keywords and is_unread:
                        logger.info(f"URGENT message detected from {sender}")
                        
                        # Roman Urdu: Message save karna
                        filepath = self.save_urgent_message(
                            sender=sender,
                            message=message_text,
                            keywords=keywords,
                            timestamp=msg.get('timestamp')
                        )

                        if filepath:
                            messages_found += 1
                            self.processed_messages.add(message_id)

                # Roman Urdu: Check count increment
                check_count += 1

                # Roman Urdu: Status log
                if check_count % 10 == 0:
                    logger.info(f"Status: {check_count} checks, {messages_found} urgent messages found")

                # Roman Urdu: Wait for next check
                time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user")

        except Exception as e:
            error_msg = f"Monitoring error: {str(e)}"
            logger.error(error_msg)
            log_error("MONITORING_ERROR", str(e),
                     action="monitor_messages", source="whatsapp_watcher")

        finally:
            # Roman Urdu: Final summary
            logger.info("=" * 60)
            logger.info("Monitoring Summary")
            logger.info("=" * 60)
            logger.info(f"Total checks: {check_count}")
            logger.info(f"Urgent messages found: {messages_found}")
            logger.info(f"Folder: {WHATSAPP_DIR}")

            # Roman Urdu: Audit log
            log_task_complete("WhatsApp Monitoring", result="COMPLETED",
                             steps_completed=str(check_count),
                             source="whatsapp_watcher")

    def cleanup(self):
        """
        Cleanup browser and resources
        Browser aur resources ko cleanup karna
        """
        # Roman Urdu: Cleanup log
        logger.info("Cleaning up resources...")

        try:
            # Roman Urdu: Browser close karna
            if self.browser:
                self.browser.close()
                logger.info("Browser closed")

            # Roman Urdu: Playwright stop karna
            if self.playwright:
                self.playwright.stop()
                logger.info("Playwright stopped")

        except Exception as e:
            error_msg = f"Cleanup error: {str(e)}"
            logger.error(error_msg)

    def __del__(self):
        """
        Destructor - cleanup on exit
        Exit par cleanup karna
        """
        self.cleanup()


def quick_monitor(duration: int = 300, headless: bool = False):
    """
    Quick function to start monitoring
    Monitoring start karne ka quick function

    Args:
        duration: Monitoring duration in seconds
        headless: Run browser without UI

    Returns:
        WhatsAppWatcher instance
    """
    # Roman Urdu: Watcher create karna
    watcher = WhatsAppWatcher(headless=headless)

    try:
        # Roman Urdu: Browser start karna
        watcher.start_browser()

        # Roman Urdu: WhatsApp load hone ka wait karna
        watcher.wait_for_whatsapp_load(timeout=120)

        # Roman Urdu: Monitoring start karna
        watcher.monitor_messages(duration=duration)

    except KeyboardInterrupt:
        logger.info("Stopping...")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        watcher.cleanup()

    return watcher


def main():
    """
    Main function with interactive setup
    Interactive setup ke saath main function
    """
    print("=" * 60)
    print("WhatsApp Watcher - AI Employee System")
    print("=" * 60)
    print()

    # Roman Urdu: Display keywords
    print("Monitoring for urgent keywords:")
    for i, keyword in enumerate(URGENT_KEYWORDS, 1):
        print(f"  {i}. {keyword}")
    print()

    # Roman Urdu: Mode selection
    print("Choose mode:")
    print("1. Quick Test (5 minutes)")
    print("2. Extended Monitoring (30 minutes)")
    print("3. Continuous Monitoring (until stopped)")
    print("4. Custom Duration")
    print()

    choice = input("Enter choice (1-4, default=2): ").strip()

    # Roman Urdu: Duration set karna
    if choice == "1":
        duration = 300  # 5 minutes
    elif choice == "3":
        duration = None  # Infinite
    elif choice == "4":
        try:
            minutes = int(input("Enter duration in minutes: ").strip())
            duration = minutes * 60
        except ValueError:
            duration = 1800  # Default 30 minutes
    else:
        duration = 1800  # Default 30 minutes

    # Roman Urdu: Headless mode
    print()
    headless_choice = input("Run in background (no browser window)? (y/n, default=n): ").strip().lower()
    headless = headless_choice == 'y'

    print()
    print("-" * 60)
    print("Starting WhatsApp Watcher...")
    print("QR code scan karein agar display ho")
    print("-" * 60)
    print()

    # Roman Urdu: Monitoring start karna
    quick_monitor(duration=duration, headless=headless)

    print()
    print("=" * 60)
    print("WhatsApp Watcher Complete")
    print("=" * 60)
    print(f"Check folder: {WHATSAPP_DIR}")
    print("Log file: whatsapp_watcher.log")
    print("=" * 60)


if __name__ == "__main__":
    main()
