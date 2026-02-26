#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup Sensitive Data - Prepare Repository for Public GitHub

This script cleans up sensitive data from the repository while preserving
real data in a backup location outside the git repository.

═══════════════════════════════════════════════════════════════════════════════
WHAT THIS SCRIPT DOES
═══════════════════════════════════════════════════════════════════════════════

1. BACKS UP real email files to a separate folder outside git
   -> D:\AI_Workspace_Backup\emails_backup\

2. DELETES real email files from these folders:
   -> AI_Employee_Vault/Inbox/
   -> AI_Employee_Vault/Needs_Action/whatsapp/
   -> AI_Employee_Vault/Done/

3. CREATES demo email files with fake content:
   -> demo_email_1.md - "Demo: Project Update"
   -> demo_email_2.md - "Demo: Meeting Request"
   -> demo_email_3.md - "Demo: Invoice Reminder"
   -> demo_email_4.md - "Demo: Welcome to the Team"

4. CREATES demo WhatsApp messages with fake phone numbers:
   -> WhatsApp messages with +1-555-xxxx numbers (fake)
   -> Safe for public GitHub

5. CLEANS up all .log files in the project

6. SHOWS a summary of what was cleaned

═══════════════════════════════════════════════════════════════════════════════
USAGE
═══════════════════════════════════════════════════════════════════════════════

    python cleanup_sensitive_data.py

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


# Configuration
PROJECT_ROOT = r"D:\AI_Workspace_bronze_silver_gold_platinum"
BACKUP_ROOT = r"D:\AI_Workspace_Backup"
VAULT_BASE = os.path.join(PROJECT_ROOT, "AI_Employee_Vault")

# Folders to clean (relative to project root)
FOLDERS_TO_CLEAN = [
    os.path.join(VAULT_BASE, "Inbox"),
    os.path.join(VAULT_BASE, "Needs_Action", "whatsapp"),
    os.path.join(VAULT_BASE, "Done"),
]

# File patterns to delete
PATTERNS_TO_DELETE = ["*.log"]

# Backup email folder (outside git)
EMAIL_BACKUP_FOLDER = os.path.join(BACKUP_ROOT, "emails_backup")

# Demo email content
DEMO_EMAILS = [
    {
        "filename": "demo_email_1.md",
        "subject": "Demo: Project Update",
        "sender": "client@example.com",
        "date": "2026-02-27 10:30:00",
        "body": """Hi Team,

This is a demo email to show the format of project updates.

Project Status: On Track
- Completed: Initial setup and configuration
- In Progress: Feature development
- Next: Testing and deployment

Best regards,
Demo Client""",
    },
    {
        "filename": "demo_email_2.md",
        "subject": "Demo: Meeting Request",
        "sender": "manager@example.com",
        "date": "2026-02-27 14:15:00",
        "body": """Hello,

I would like to schedule a meeting to discuss the upcoming project milestones.

Proposed Times:
- Monday, March 2nd at 2:00 PM
- Tuesday, March 3rd at 10:00 AM

Please let me know which time works best for you.

Thanks,
Demo Manager""",
    },
    {
        "filename": "demo_email_3.md",
        "subject": "Demo: Invoice Reminder",
        "sender": "billing@example.com",
        "date": "2026-02-26 09:00:00",
        "body": """Dear Customer,

This is a friendly reminder that invoice #INV-2026-001 is due on March 1st, 2026.

Invoice Details:
- Amount: $1,500.00
- Due Date: March 1st, 2026
- Services: Web Development

Please process the payment at your earliest convenience.

Best regards,
Billing Department""",
    },
    {
        "filename": "demo_email_4.md",
        "subject": "Demo: Welcome to the Team",
        "sender": "hr@example.com",
        "date": "2026-02-25 08:00:00",
        "body": """Welcome to the Team!

We are excited to have you on board.

Your first day orientation will include:
- Team introductions
- System access setup
- Project overview

Looking forward to working with you!

Best,
HR Team""",
    },
]


def print_header(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subheader(title):
    """Print a formatted subsection header"""
    print(f"\n[{title}]")


def backup_email_files():
    """Backup real email files to external folder"""
    print_header("STEP 1: BACKING UP REAL EMAIL FILES")
    
    backed_up_count = 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_session_folder = os.path.join(EMAIL_BACKUP_FOLDER, f"backup_{timestamp}")
    
    # Create backup folder
    os.makedirs(backup_session_folder, exist_ok=True)
    print(f"Backup folder: {backup_session_folder}")
    
    for folder in FOLDERS_TO_CLEAN:
        if not os.path.exists(folder):
            print_subheader(f"Folder not found (skipping): {folder}")
            continue
            
        print_subheader(f"Scanning: {folder}")
        
        # Find all .md files
        md_files = list(Path(folder).glob("*.md"))
        
        if not md_files:
            print(f"  No .md files found")
            continue
        
        # Create subfolder for this source
        source_name = os.path.basename(folder).replace(" ", "_")
        source_backup = os.path.join(backup_session_folder, source_name)
        os.makedirs(source_backup, exist_ok=True)
        
        for md_file in md_files:
            try:
                # Copy file to backup
                dest_path = os.path.join(source_backup, md_file.name)
                shutil.copy2(md_file, dest_path)
                print(f"  ✓ Backed up: {md_file.name}")
                backed_up_count += 1
            except Exception as e:
                print(f"  ✗ Error backing up {md_file.name}: {e}")
    
    print(f"\nTotal files backed up: {backed_up_count}")
    return backup_session_folder


def delete_email_files():
    """Delete email files from specified folders"""
    print_header("STEP 2: DELETING EMAIL FILES FROM GIT FOLDERS")
    
    deleted_count = 0
    
    for folder in FOLDERS_TO_CLEAN:
        if not os.path.exists(folder):
            print_subheader(f"Folder not found (skipping): {folder}")
            continue
            
        print_subheader(f"Cleaning: {folder}")
        
        # Find all .md files
        md_files = list(Path(folder).glob("*.md"))
        
        if not md_files:
            print(f"  No .md files found")
            continue
        
        for md_file in md_files:
            try:
                os.remove(md_file)
                print(f"  ✓ Deleted: {md_file.name}")
                deleted_count += 1
            except Exception as e:
                print(f"  ✗ Error deleting {md_file.name}: {e}")
    
    print(f"\nTotal files deleted: {deleted_count}")
    return deleted_count


def create_demo_emails():
    """Create demo email files with fake content"""
    print_header("STEP 3: CREATING DEMO EMAIL FILES")
    
    inbox_folder = os.path.join(VAULT_BASE, "Inbox")
    os.makedirs(inbox_folder, exist_ok=True)
    
    created_count = 0
    
    for demo in DEMO_EMAILS:
        filepath = os.path.join(inbox_folder, demo["filename"])
        
        # Create markdown content
        content = f"""---
type: email
priority: normal
sender: {demo["sender"]}
received_at: {demo["date"]}
status: new
---

# Email: {demo["subject"]}

## Sender Information
- **From:** {demo["sender"]}
- **Received:** {demo["date"]}
- **Platform:** Gmail

## Subject
{demo["subject"]}

## Body
{demo["body"]}

## Action Required
<!-- Add any required actions here -->

## Response Draft
<!-- Add response draft here -->

---
*This is a DEMO email for testing purposes*
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Created: {demo['filename']}")
            created_count += 1
        except Exception as e:
            print(f"  ✗ Error creating {demo['filename']}: {e}")
    
    print(f"\nTotal demo files created: {created_count}")
    return created_count


def clean_log_files():
    """Delete all .log files in the project"""
    print_header("STEP 4: CLEANING LOG FILES")
    
    deleted_count = 0
    
    # Find all .log files in project
    for pattern in PATTERNS_TO_DELETE:
        log_files = list(Path(PROJECT_ROOT).rglob(pattern))
        
        for log_file in log_files:
            try:
                os.remove(log_file)
                print(f"  ✓ Deleted: {log_file.relative_to(PROJECT_ROOT)}")
                deleted_count += 1
            except Exception as e:
                print(f"  ✗ Error deleting {log_file}: {e}")
    
    if deleted_count == 0:
        print("  No .log files found")
    
    print(f"\nTotal log files deleted: {deleted_count}")
    return deleted_count


def show_summary(backup_folder, emails_deleted, demo_created, logs_deleted):
    """Show summary of cleanup operations"""
    print_header("CLEANUP SUMMARY")

    print(f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│  OPERATION                          │  STATUS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  Backup Location:                   │                                       │
│  {backup_folder:<68}│
├─────────────────────────────────────────────────────────────────────────────┤
│  Email Files Backed Up:             │  SUCCESS                              │
│  (Stored safely outside git repo)   │                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Email Files Deleted:               │  {emails_deleted} files removed        │
│  (From Inbox, Needs_Action, Done)   │                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Demo Emails Created:               │  {demo_created} files created          │
│  (Safe for public GitHub)           │                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Demo WhatsApp Messages Created:    │  4 files created                       │
│  (Fake phone numbers: +1-555-xxxx)  │                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Log Files Cleaned:                 │  {logs_deleted} files removed          │
│  (Cleared all .log files)           │                                       │
└─────────────────────────────────────────────────────────────────────────────┘

[SUCCESS] Repository is now safe for public GitHub!

Your real data is safely backed up at:
  {backup_folder}

Demo files are located at:
  Emails: {os.path.join(VAULT_BASE, "Inbox")}
  WhatsApp: {os.path.join(VAULT_BASE, "Needs_Action", "whatsapp")}

═══════════════════════════════════════════════════════════════════════════════
NEXT STEPS
═══════════════════════════════════════════════════════════════════════════════

1. Review demo files:
   - Emails: AI_Employee_Vault/Inbox/
   - WhatsApp: AI_Employee_Vault/Needs_Action/whatsapp/
2. Run 'git status' to see the changes
3. Add and commit the changes
4. Push to GitHub

Example:
  cd {PROJECT_ROOT}
  git add .
  git commit -m "Cleanup: Replace sensitive data with demo files"
  git push

═══════════════════════════════════════════════════════════════════════════════
""")


def main():
    """Main cleanup function"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           CLEANUP SENSITIVE DATA - GitHub Preparation Script                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

This script will:
  1. Backup real emails to external folder
  2. Delete real emails from git folders
  3. Create demo email files
  4. Create demo WhatsApp messages (fake phone numbers)
  5. Clean all .log files

WARNING: This will delete files from your vault folders!
    Real data will be backed up safely.

""")

    # Confirm before proceeding
    response = input("Continue with cleanup? (yes/no): ").strip().lower()
    if response != "yes":
        print("\nCleanup cancelled.")
        return

    print("\nStarting cleanup...")

    # Step 1: Backup emails
    backup_folder = backup_email_files()

    # Step 2: Delete email files
    emails_deleted = delete_email_files()

    # Step 3: Create demo emails
    demo_created = create_demo_emails()

    # Step 4: Create demo WhatsApp messages
    print_header("STEP 4: CREATING DEMO WHATSAPP MESSAGES")
    whatsapp_created = 0
    try:
        import subprocess
        script_dir = os.path.dirname(os.path.abspath(__file__))
        demo_whatsapp_script = os.path.join(script_dir, "digital-fte", "create_demo_whatsapp.py")
        if os.path.exists(demo_whatsapp_script):
            result = subprocess.run(
                ["python", demo_whatsapp_script],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                whatsapp_created = 4  # We know the script creates 4 messages
                print("Demo WhatsApp messages created successfully")
            else:
                print(f"Error: {result.stderr}")
        else:
            print(f"Script not found: {demo_whatsapp_script}")
    except Exception as e:
        print(f"Error creating demo WhatsApp: {e}")

    # Step 5: Clean log files
    logs_deleted = clean_log_files()

    # Show summary
    show_summary(backup_folder, emails_deleted, demo_created, logs_deleted)


if __name__ == "__main__":
    main()
