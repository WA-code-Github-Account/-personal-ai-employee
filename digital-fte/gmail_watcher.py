#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Email Monitor for wahishaikh545@gmail.com

═══════════════════════════════════════════════════════════════════════════════
📧 SETUP INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════

Current Account: wahishaikh545@gmail.com

Step 1: Delete Old Token (if switching from previous account)
─────────────────────────────────────────────────────────────
Delete token.pickle file from this directory:
    D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte\token.pickle

This forces re-authentication with the new account.
Command: del D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte\token.pickle

Step 2: Ensure credentials.json Exists
─────────────────────────────────────────────────────────────
Place your credentials.json file in this directory:
    D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte\credentials.json

Download from Google Cloud Console:
    https://console.cloud.google.com/apis/credentials
    → Create OAuth 2.0 Client ID → Desktop App → Download JSON

Step 3: Run Gmail Watcher
─────────────────────────────────────────────────────────────
    cd D:\AI_Workspace_bronze_silver_gold_platinum\digital-fte
    python gmail_watcher.py

Step 4: Authorize in Browser
─────────────────────────────────────────────────────────────
- Browser will open automatically
- Sign in with: wahishaikh545@gmail.com
- Grant permissions to the application
- token.pickle will be created automatically

Step 5: Verification
─────────────────────────────────────────────────────────────
- Check that token.pickle is created in this directory
- Verify emails are being saved to: AI_Employee_Vault/Inbox/

═══════════════════════════════════════════════════════════════════════════════
⚠️ TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

• Wrong account authenticated?
  → Delete token.pickle and run again

• credentials.json not found?
  → Download from Google Cloud Console (see Step 2)

• Authentication failed?
  → Ensure Gmail API is enabled in Google Cloud Console

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import pickle
import time
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

# Scopes required for reading and modifying Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Configuration: Target email account
TARGET_EMAIL = "wahishaikh545@gmail.com"

def authenticate_gmail():
    """
    Authenticate and return Gmail service object for wahishaikh545@gmail.com
    
    Returns:
        Gmail service object or None if authentication fails
    """
    creds = None

    # Token file stores the user's access and refresh tokens
    # Located in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, 'token.pickle')
    credentials_path = os.path.join(script_dir, 'credentials.json')

    # Load existing token if available
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        print(f"Loaded existing token from: {token_path}")

    # If there are no valid credentials, request authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            # No valid token - need to re-authenticate
            if not os.path.exists(credentials_path):
                print(f"ERROR: credentials.json not found at: {credentials_path}")
                print(f"\nPlease download your credentials.json file from Google Cloud Console:")
                print(f"  1. Visit: https://console.cloud.google.com/apis/credentials")
                print(f"  2. Create OAuth 2.0 Client ID (Desktop App)")
                print(f"  3. Download the JSON file")
                print(f"  4. Save it as: {credentials_path}")
                return None

            print(f"\n{'='*60}")
            print(f"AUTHORIZATION REQUIRED")
            print(f"{'='*60}")
            print(f"Target Account: {TARGET_EMAIL}")
            print(f"{'='*60}")
            print(f"\nA browser window will open shortly.")
            print(f"Please sign in with: {TARGET_EMAIL}")
            print(f"\nIf wrong account opens, sign out and select: {TARGET_EMAIL}")
            print(f"{'='*60}\n")

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        print(f"Token saved to: {token_path}")

    return build('gmail', 'v1', credentials=creds)


def decode_email_body(payload):
    """Decode email body from base64 encoding"""
    if 'body' in payload and 'data' in payload['body']:
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    elif 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    return ''


def get_unread_emails(service, max_results=10):
    """Get unread emails from Gmail"""
    try:
        # Query for unread emails
        results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg in messages:
            msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
            
            # Extract headers
            headers = msg_detail['payload']['headers']
            sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown')
            subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
            date = next((header['value'] for header in headers if header['name'].lower() == 'date'), 'Unknown Date')
            
            # Extract body
            body = decode_email_body(msg_detail['payload'])
            
            email_data = {
                'id': msg['id'],
                'sender': sender,
                'subject': subject,
                'date': date,
                'body': body
            }
            
            emails.append(email_data)
        
        return emails
    
    except Exception as e:
        print(f"An error occurred while fetching emails: {e}")
        return []


def save_email_as_markdown(email_data, inbox_folder):
    """Save email data as a markdown file in the inbox folder"""
    try:
        # Create a safe filename from the subject
        safe_subject = "".join(c for c in email_data['subject'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_subject:
            safe_subject = f"email_{email_data['id']}"
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{safe_subject[:50]}.md"
        filepath = os.path.join(inbox_folder, filename)
        
        # Create markdown content
        markdown_content = f"""# Email from: {email_data['sender']}

**Subject:** {email_data['subject']}

**Date:** {email_data['date']}

---

## Body:
{email_data['body']}
"""
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Saved email to: {filepath}")
        return filepath
    
    except Exception as e:
        print(f"Error saving email as markdown: {e}")
        return None


def mark_email_as_read(service, email_id):
    """Mark an email as read"""
    try:
        # Modify the message to remove the 'UNREAD' label
        service.users().messages().modify(
            userId='me',
            id=email_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        print(f"Marked email {email_id} as read")
    except Exception as e:
        print(f"Error marking email as read: {e}")


def main():
    """Main function to run the Gmail watcher"""
    # Define the inbox folder path
    inbox_folder = os.path.join('..', 'AI_Employee_Vault', 'Inbox')

    # Create inbox folder if it doesn't exist
    os.makedirs(inbox_folder, exist_ok=True)

    print(f"{'='*60}")
    print(f"Gmail Watcher - AI Employee System")
    print(f"{'='*60}")
    print(f"Target Account: {TARGET_EMAIL}")
    print(f"Monitoring Folder: {inbox_folder}")
    print(f"{'='*60}")
    print()
    print("Authenticating with Gmail...")
    service = authenticate_gmail()

    if not service:
        print("Failed to authenticate with Gmail. Exiting.")
        return

    print(f"Successfully authenticated with Gmail.")
    
    while True:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for unread emails...")
        
        # Get unread emails
        emails = get_unread_emails(service)
        
        if emails:
            print(f"Found {len(emails)} unread email(s)")
            
            for email in emails:
                # Save email as markdown file
                saved_file = save_email_as_markdown(email, inbox_folder)
                
                if saved_file:
                    # Mark email as read after saving
                    mark_email_as_read(service, email['id'])
                else:
                    print(f"Failed to save email: {email['subject']}")
        else:
            print("No unread emails found.")
        
        print(f"Waiting 5 minutes before next check...")
        time.sleep(300)  # Wait for 5 minutes (300 seconds)


if __name__ == '__main__':
    main()