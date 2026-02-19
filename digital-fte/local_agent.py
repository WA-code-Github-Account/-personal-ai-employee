#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Agent - Platinum Tier
Handles: Approvals, Final Send Actions, WhatsApp, Payments
Domain: /Needs_Action/local/
Claim-by-move rule: Moves tasks to In_Progress when claimed
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from skills.vault_skill import read_file, write_file, move_file, list_folder

# Roman Urdu: Configuration aur global variables
VAULT_PATH = "D:/AI_Workspace/AI_Employee_Vault"
LOCAL_DOMAIN = "Needs_Action/local"
AGENT_NAME = "Local-Agent"
LOG_FILE = "agent.log"

# Roman Urdu: Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LocalAgent:
    """
    Local Agent for Platinum Tier
    Handles sensitive local actions: approvals, sending, WhatsApp, payments
    Domain ownership: /Needs_Action/local/
    """

    def __init__(self):
        """
        Initialize Local Agent
        Roman Urdu: Local Agent ko initialize karna
        """
        self.vault_path = Path(VAULT_PATH)
        self.local_domain = self.vault_path / LOCAL_DOMAIN
        self.in_progress = self.vault_path / "In_Progress"
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.done = self.vault_path / "Done"
        
        # Roman Urdu: Ensure directories exist
        self._ensure_domains_exists()
        
        logger.info(f"Local Agent initialized. Domain: {LOCAL_DOMAIN}")

    def _ensure_domains_exists(self):
        """
        Ensure local domain and related directories exist
        Roman Urdu: Local domain aur related directories ko ensure karna
        """
        for directory in [self.local_domain, self.in_progress, self.pending_approval, self.done]:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory.name}")

    def claim_task(self, filename):
        """
        Claim a task by moving it from local domain to In_Progress
        Roman Urdu: Task ko claim karna by moving to In_Progress
        
        Args:
            filename (str): Name of the task file to claim
            
        Returns:
            bool: True if successful, False otherwise
        """
        source = self.local_domain / filename
        dest = self.in_progress / filename
        
        if not source.exists():
            # Roman Urdu: Check Pending_Approval mein bhi
            source = self.pending_approval / filename
            if not source.exists():
                logger.error(f"Task not found in local domain or pending approval: {filename}")
                return False
        
        try:
            # Roman Urdu: File ko In_Progress mein move karna
            success = move_file(str(source), str(dest))
            if success:
                logger.info(f"Claimed task: {filename} -> In_Progress")
                # Roman Urdu: Claim metadata add karna
                self._add_claim_metadata(dest, "local")
            return success
        except Exception as e:
            logger.error(f"Error claiming task {filename}: {str(e)}")
            return False

    def _add_claim_metadata(self, file_path, agent_type):
        """
        Add claim metadata to task file
        Roman Urdu: Task file mein claim metadata add karna
        
        Args:
            file_path (Path): Path to the task file
            agent_type (str): Type of agent claiming ("cloud" or "local")
        """
        try:
            content = read_file(str(file_path))
            if content:
                # Roman Urdu: Metadata header add karna
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                metadata = f"""---
claimed_by: {agent_type}
claimed_at: {timestamp}
status: in_progress
---

"""
                # Roman Urdu: Existing content ke saath metadata merge karna
                if not content.startswith("---"):
                    updated_content = metadata + content
                else:
                    updated_content = content
                write_file(str(file_path), updated_content)
                logger.info(f"Added claim metadata to {file_path.name}")
        except Exception as e:
            logger.error(f"Error adding metadata: {str(e)}")

    def approve_task(self, filename, approval_notes=None):
        """
        Approve a task and move it to Pending_Approval or mark as approved
        Roman Urdu: Task ko approve karna
        
        Args:
            filename (str): Name of the task file to approve
            approval_notes (str): Optional notes about the approval
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = self.in_progress / filename
        
        if not file_path.exists():
            file_path = self.local_domain / filename
        
        if not file_path.exists():
            logger.error(f"Task not found for approval: {filename}")
            return False
        
        try:
            content = read_file(str(file_path))
            
            # Roman Urdu: Status update karna
            updated_content = content.replace("status: draft", "status: approved")
            updated_content = updated_content.replace("status: pending", "status: approved")
            updated_content = updated_content.replace("status: in_progress", "status: approved")
            
            # Roman Urdu: Approval metadata add karna
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            approval_section = f"""
## Approval
- **Approved at:** {timestamp}
- **Approved by:** Local Agent
"""
            if approval_notes:
                approval_section += f"- **Notes:** {approval_notes}\n"
            
            updated_content += approval_section
            
            # Roman Urdu: File ko Pending_Approval mein move karna
            dest = self.pending_approval / filename
            write_file(str(file_path), updated_content)
            move_file(str(file_path), str(dest))
            
            logger.info(f"Task approved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error approving task: {str(e)}")
            return False

    def reject_task(self, filename, rejection_reason):
        """
        Reject a task and add rejection reason
        Roman Urdu: Task ko reject karna
        
        Args:
            filename (str): Name of the task file
            rejection_reason (str): Reason for rejection
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = self.in_progress / filename
        
        if not file_path.exists():
            file_path = self.local_domain / filename
        
        if not file_path.exists():
            logger.error(f"Task not found for rejection: {filename}")
            return False
        
        try:
            content = read_file(str(file_path))
            
            # Roman Urdu: Status update karna
            updated_content = content.replace("status: draft", "status: rejected")
            updated_content = updated_content.replace("status: pending", "status: rejected")
            updated_content = updated_content.replace("status: in_progress", "status: rejected")
            
            # Roman Urdu: Rejection metadata add karna
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rejection_section = f"""
## Rejection
- **Rejected at:** {timestamp}
- **Rejected by:** Local Agent
- **Reason:** {rejection_reason}

"""
            updated_content += rejection_section
            
            write_file(str(file_path), updated_content)
            
            # Roman Urdu: File ko wapis local domain mein bhejna for revision
            dest = self.local_domain / filename
            if str(dest) != str(file_path):
                move_file(str(file_path), str(dest))
            
            logger.info(f"Task rejected: {filename} - {rejection_reason}")
            return True
        except Exception as e:
            logger.error(f"Error rejecting task: {str(e)}")
            return False

    def finalize_send(self, filename, send_channel):
        """
        Finalize and send a task (email, social post, etc.)
        Roman Urdu: Task ko finalize karke bhejna
        
        Args:
            filename (str): Name of the task file
            send_channel (str): Channel to send through (email, social, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = self.pending_approval / filename
        
        if not file_path.exists():
            file_path = self.in_progress / filename
        
        if not file_path.exists():
            logger.error(f"Task not found for sending: {filename}")
            return False
        
        try:
            content = read_file(str(file_path))
            
            # Roman Urdu: Send metadata add karna
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            send_section = f"""
## Sent
- **Sent at:** {timestamp}
- **Channel:** {send_channel}
- **Sent by:** Local Agent
- **Status:** DELIVERED

"""
            updated_content = content + send_section
            
            # Roman Urdu: Status update karna
            updated_content = updated_content.replace("status: approved", "status: sent")
            
            write_file(str(file_path), updated_content)
            
            # Roman Urdu: File ko Done folder mein move karna
            dest = self.done / filename
            move_file(str(file_path), str(dest))
            
            logger.info(f"Task sent via {send_channel}: {filename} -> Done")
            return True
        except Exception as e:
            logger.error(f"Error finalizing send: {str(e)}")
            return False

    def create_payment_task(self, payment_data):
        """
        Create a payment task in local domain
        Roman Urdu: Payment task banana
        
        Args:
            payment_data (dict): Payment data with amount, recipient, purpose, etc.
            
        Returns:
            str: Filename of created task, or None if failed
        """
        # Roman Urdu: Unique filename generate karna
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recipient_slug = payment_data.get("recipient", "unknown")[:30].replace(" ", "_")
        filename = f"payment_{timestamp}_{recipient_slug}.md"
        
        # Roman Urdu: Payment task content
        content = f"""---
type: payment_task
domain: local
priority: {payment_data.get('priority', 'normal')}
amount: {payment_data.get('amount', 0)}
currency: {payment_data.get('currency', 'PKR')}
recipient: {payment_data.get('recipient', 'Unknown')}
purpose: {payment_data.get('purpose', 'General Payment')}
created_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
status: pending_approval
requires_approval: true
---

# Payment Task

## Payment Details
- **Recipient:** {payment_data.get('recipient', 'Unknown')}
- **Amount:** {payment_data.get('currency', 'PKR')} {payment_data.get('amount', 0)}
- **Purpose:** {payment_data.get('purpose', 'General Payment')}
- **Due Date:** {payment_data.get('due_date', 'N/A')}
- **Payment Method:** {payment_data.get('method', 'Bank Transfer')}

## Invoice/Reference
{payment_data.get('invoice_number', 'N/A')}

## Notes
{payment_data.get('notes', 'No additional notes')}

## Approval Required
<!-- Local Agent: Payment approval ke liye bheja gaya -->

"""
        
        file_path = self.local_domain / filename
        success = write_file(str(file_path), content)
        
        if success:
            logger.info(f"Created payment task: {filename}")
            return filename
        else:
            logger.error(f"Failed to create payment task: {filename}")
            return None

    def process_payment_approval(self, filename, approved_by, approval_code=None):
        """
        Process payment approval with optional approval code
        Roman Urdu: Payment approval process karna
        
        Args:
            filename (str): Payment task filename
            approved_by (str): Name of approver
            approval_code (str): Optional approval code/OTP
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = self.local_domain / filename
        
        if not file_path.exists():
            file_path = self.pending_approval / filename
        
        if not file_path.exists():
            logger.error(f"Payment task not found: {filename}")
            return False
        
        try:
            content = read_file(str(file_path))
            
            # Roman Urdu: Approval metadata add karna
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            approval_section = f"""
## Payment Approval
- **Approved at:** {timestamp}
- **Approved by:** {approved_by}
"""
            if approval_code:
                approval_section += f"- **Approval Code:** {approval_code}\n"
            
            approval_section += "- **Status:** APPROVED_FOR_PAYMENT\n"
            
            updated_content = content + approval_section
            updated_content = updated_content.replace("status: pending_approval", "status: approved_for_payment")
            
            write_file(str(file_path), updated_content)
            
            logger.info(f"Payment approved: {filename} by {approved_by}")
            return True
        except Exception as e:
            logger.error(f"Error processing payment approval: {str(e)}")
            return False

    def create_whatsapp_message(self, message_data):
        """
        Create a WhatsApp message task
        Roman Urdu: WhatsApp message task banana
        
        Args:
            message_data (dict): Message data with contact, message, media
            
        Returns:
            str: Filename of created task, or None if failed
        """
        # Roman Urdu: Unique filename generate karna
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        contact_slug = message_data.get("contact", "unknown")[:30].replace(" ", "_")
        filename = f"whatsapp_{timestamp}_{contact_slug}.md"
        
        # Roman Urdu: WhatsApp task content
        content = f"""---
type: whatsapp_task
domain: local
contact: {message_data.get('contact', 'Unknown')}
contact_number: {message_data.get('number', 'N/A')}
message_type: {message_data.get('type', 'text')}
priority: {message_data.get('priority', 'normal')}
created_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
status: pending
requires_approval: true
---

# WhatsApp Message Task

## Recipient
- **Contact:** {message_data.get('contact', 'Unknown')}
- **Number:** {message_data.get('number', 'N/A')}

## Message Content
{message_data.get('message', '')}

## Media Attachments
{chr(10).join(f'- {attachment}' for attachment in message_data.get('media', [])) or 'None'}

## Send Schedule
- **Send At:** {message_data.get('schedule', 'Immediate')}
- **Reminder:** {message_data.get('reminder', 'None')}

## Approval Required
<!-- Local Agent: WhatsApp message approval ke liye bheja gaya -->

"""
        
        file_path = self.local_domain / filename
        success = write_file(str(file_path), content)
        
        if success:
            logger.info(f"Created WhatsApp task: {filename}")
            return filename
        else:
            logger.error(f"Failed to create WhatsApp task: {filename}")
            return None

    def send_whatsapp_message(self, filename):
        """
        Send a WhatsApp message (placeholder for actual WhatsApp API)
        Roman Urdu: WhatsApp message bhejna
        
        Args:
            filename (str): WhatsApp task filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = self.pending_approval / filename
        
        if not file_path.exists():
            file_path = self.in_progress / filename
        
        if not file_path.exists():
            logger.error(f"WhatsApp task not found: {filename}")
            return False
        
        try:
            content = read_file(str(file_path))
            
            # Roman Urdu: Send metadata add karna (placeholder for actual API call)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            send_section = f"""
## Sent via WhatsApp
- **Sent at:** {timestamp}
- **Status:** DELIVERED (placeholder)
- **Sent by:** Local Agent

"""
            updated_content = content + send_section
            updated_content = updated_content.replace("status: approved", "status: sent")
            
            write_file(str(file_path), updated_content)
            
            # Roman Urdu: File ko Done folder mein move karna
            dest = self.done / filename
            move_file(str(file_path), str(dest))
            
            logger.info(f"WhatsApp message sent: {filename} -> Done")
            return True
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return False

    def list_pending_approvals(self):
        """
        List all tasks pending approval in local domain
        Roman Urdu: Pending approvals ki list
        
        Returns:
            list: List of pending approval filenames
        """
        tasks = []
        if self.pending_approval.exists():
            files = list_folder(str(self.pending_approval))
            for file in files:
                if file.endswith(".md"):
                    tasks.append(file)
        
        logger.info(f"Found {len(tasks)} pending approvals")
        return tasks

    def list_local_tasks(self):
        """
        List all tasks in local domain
        Roman Urdu: Local domain tasks ki list
        
        Returns:
            list: List of local task filenames
        """
        tasks = []
        if self.local_domain.exists():
            files = list_folder(str(self.local_domain))
            for file in files:
                if file.endswith(".md"):
                    tasks.append(file)
        
        logger.info(f"Found {len(tasks)} tasks in local domain")
        return tasks

    def get_task_status(self, filename):
        """
        Get status of a specific task
        Roman Urdu: Specific task ka status check karna
        
        Args:
            filename (str): Name of the task file
            
        Returns:
            dict: Task status and metadata, or None if not found
        """
        # Roman Urdu: Multiple locations check karna
        possible_locations = [
            self.local_domain / filename,
            self.in_progress / filename,
            self.pending_approval / filename,
            self.done / filename
        ]
        
        file_path = None
        location_name = None
        
        for path in possible_locations:
            if path.exists():
                file_path = path
                location_name = path.parent.name
                break
        
        if not file_path:
            logger.error(f"Task not found: {filename}")
            return None
        
        try:
            content = read_file(str(file_path))
            
            # Roman Urdu: Frontmatter metadata parse karna
            metadata = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 2:
                    frontmatter = parts[1].strip()
                    for line in frontmatter.split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            metadata[key.strip()] = value.strip()
            
            return {
                "filename": filename,
                "metadata": metadata,
                "location": location_name,
                "full_path": str(file_path)
            }
        except Exception as e:
            logger.error(f"Error reading task status: {str(e)}")
            return None

    def transfer_from_cloud(self, cloud_filename, reason=""):
        """
        Transfer a task from cloud domain to local domain
        Roman Urdu: Cloud se local domain mein task transfer karna
        
        Args:
            cloud_filename (str): Name of the task file in cloud domain
            reason (str): Reason for transfer
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Roman Urdu: Cloud domain se file uthana
        cloud_path = self.vault_path / "Needs_Action" / "cloud" / cloud_filename
        
        if not cloud_path.exists():
            # Roman Urdu: Check In_Progress mein bhi
            cloud_path = self.in_progress / cloud_filename
        
        if not cloud_path.exists():
            logger.error(f"Cloud task not found: {cloud_filename}")
            return False
        
        try:
            content = read_file(str(cloud_path))
            
            # Roman Urdu: Transfer metadata add karna
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            transfer_note = f"""
## Transfer to Local
- **Transferred at:** {timestamp}
- **From:** Cloud Agent
- **Reason:** {reason if reason else 'Requires local approval/action'}

"""
            updated_content = content + transfer_note
            
            # Roman Urdu: Domain update karna
            updated_content = updated_content.replace("domain: cloud", "domain: local")
            
            write_file(str(cloud_path), updated_content)
            
            # Roman Urdu: Local domain mein move karna
            dest = self.local_domain / cloud_filename
            move_file(str(cloud_path), str(dest))
            
            logger.info(f"Transferred from cloud: {cloud_filename} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Error transferring task: {str(e)}")
            return False

    def process_cloud_handoff(self, cloud_task_filename):
        """
        Process a task handed off from Cloud Agent
        Roman Urdu: Cloud Agent se handed off task ko process karna
        
        Args:
            cloud_task_filename (str): Name of the task from cloud
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Roman Urdu: Pehle cloud se local transfer karna
        if not self.transfer_from_cloud(cloud_task_filename, "Cloud agent requires local approval"):
            return False
        
        # Roman Urdu: Ab local domain mein claim karna
        if not self.claim_task(cloud_task_filename):
            return False
        
        logger.info(f"Processed cloud handoff: {cloud_task_filename}")
        return True


def main():
    """
    Main function to demonstrate Local Agent capabilities
    Roman Urdu: Local Agent capabilities ko demonstrate karna
    """
    print("=" * 60)
    print("Local Agent - Platinum Tier")
    print("Domain: /Needs_Action/local/")
    print("=" * 60)
    
    # Initialize agent
    agent = LocalAgent()
    
    # Demo: Create payment task
    print("\n[Demo] Creating Payment Task:")
    payment_data = {
        "recipient": "ABC Services",
        "amount": 50000,
        "currency": "PKR",
        "purpose": "Monthly Subscription",
        "invoice_number": "INV-2026-001",
        "method": "Bank Transfer",
        "priority": "high"
    }
    payment_file = agent.create_payment_task(payment_data)
    print(f"  Created: {payment_file}")
    
    # Demo: Create WhatsApp message
    print("\n[Demo] Creating WhatsApp Message:")
    whatsapp_data = {
        "contact": "Client - John Doe",
        "number": "+92-300-1234567",
        "message": "Hi! Your project update is ready for review.",
        "priority": "normal"
    }
    whatsapp_file = agent.create_whatsapp_message(whatsapp_data)
    print(f"  Created: {whatsapp_file}")
    
    # Demo: List local tasks
    print("\n[Demo] Tasks in Local Domain:")
    tasks = agent.list_local_tasks()
    for task in tasks:
        print(f"  - {task}")
    
    # Demo: List pending approvals
    print("\n[Demo] Pending Approvals:")
    approvals = agent.list_pending_approvals()
    for approval in approvals:
        print(f"  - {approval}")
    
    print("\n" + "=" * 60)
    print("Local Agent demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
