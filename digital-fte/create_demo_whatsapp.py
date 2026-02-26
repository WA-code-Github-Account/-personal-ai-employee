#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Demo WhatsApp Messages - For Hackathon Demo

Yeh script demo WhatsApp messages create karti hai jo safe hain
public GitHub ke liye. Koi real phone number ya personal data nahi.
"""

import os
from datetime import datetime

# Configuration
VAULT_BASE = r"D:\AI_Workspace_bronze_silver_gold_platinum\AI_Employee_Vault"
WHATSAPP_DIR = os.path.join(VAULT_BASE, "Needs_Action", "whatsapp")

# Demo WhatsApp Messages (Fake Data - Safe for GitHub)
DEMO_WHATSAPP_MESSAGES = [
    {
        "filename": "WhatsApp_20260227_101500_Client_Demo.md",
        "sender": "Client Demo",
        "phone": "+1-555-0123",
        "timestamp": "2026-02-27 10:15:00",
        "keywords": ["urgent", "invoice"],
        "message": """Hi! This is an urgent request. Please send the invoice for the project by end of day. Thanks!""",
    },
    {
        "filename": "WhatsApp_20260227_143000_Team_Member.md",
        "sender": "Team Member",
        "phone": "+1-555-0456",
        "timestamp": "2026-02-27 14:30:00",
        "keywords": ["asap", "help"],
        "message": """Hey! I need help with the presentation. Can you review the slides ASAP? Meeting is at 3 PM.""",
    },
    {
        "filename": "WhatsApp_20260227_090000_Support_Team.md",
        "sender": "Support Team",
        "phone": "+1-555-0789",
        "timestamp": "2026-02-27 09:00:00",
        "keywords": ["critical", "payment"],
        "message": """Critical update: Payment gateway is down. Please check immediately. Ticket #12345""",
    },
    {
        "filename": "WhatsApp_20260226_160000_Manager_Demo.md",
        "sender": "Manager Demo",
        "phone": "+1-555-0321",
        "timestamp": "2026-02-26 16:00:00",
        "keywords": ["important", "immediately"],
        "message": """Important: Please submit your timesheets immediately. HR needs them for payroll processing.""",
    },
]


def create_demo_whatsapp_messages():
    """Create demo WhatsApp message files"""
    
    # Create WhatsApp directory
    os.makedirs(WHATSAPP_DIR, exist_ok=True)
    
    print("=" * 60)
    print("Creating Demo WhatsApp Messages")
    print("=" * 60)
    print(f"Folder: {WHATSAPP_DIR}")
    print()
    
    created_count = 0
    
    for demo in DEMO_WHATSAPP_MESSAGES:
        filepath = os.path.join(WHATSAPP_DIR, demo["filename"])
        
        # Create markdown content
        content = f"""---
type: whatsapp_message
priority: urgent
keywords: {', '.join(demo['keywords'])}
sender: {demo['sender']}
phone: {demo['phone']}
received_at: {demo['timestamp']}
status: new
---

# WhatsApp Urgent Message

## Sender Information
- **Name:** {demo['sender']}
- **Phone:** {demo['phone']}
- **Received:** {demo['timestamp']}
- **Platform:** WhatsApp Web

## Message Content
{demo['message']}

## Detected Keywords
{chr(10).join(f'- {keyword}' for keyword in demo['keywords'])}

## Action Required
<!-- Yahan action likhen ke is message ka kya karna hai -->

## Response Draft
<!-- Yahan response draft likhen -->

---
*This is a DEMO WhatsApp message for hackathon testing purposes*
*No real phone numbers or personal data included*
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Created: {demo['filename']}")
            print(f"  Sender: {demo['sender']}")
            print(f"  Keywords: {', '.join(demo['keywords'])}")
            created_count += 1
        except Exception as e:
            print(f"[ERROR] Creating {demo['filename']}: {e}")
    
    print()
    print("=" * 60)
    print(f"Total demo WhatsApp messages created: {created_count}")
    print("=" * 60)
    print()
    print("[SUCCESS] Demo WhatsApp messages are ready for hackathon demo!")
    print()
    print("Next steps:")
    print("1. Open Obsidian vault: AI_Employee_Vault/")
    print("2. Navigate to: Needs_Action/whatsapp/")
    print("3. Review the demo messages")
    print("4. Show in hackathon presentation")
    print()


if __name__ == "__main__":
    create_demo_whatsapp_messages()
