#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Agent - Platinum Tier
Handles: Email Triage, Draft Replies, Social Post Drafts
Domain: /Needs_Action/cloud/
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
CLOUD_DOMAIN = "Needs_Action/cloud"
AGENT_NAME = "Cloud-Agent"
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


class CloudAgent:
    """
    Cloud Agent for Platinum Tier
    Handles external cloud-based tasks: email, social media, drafts
    Domain ownership: /Needs_Action/cloud/
    """

    def __init__(self):
        """
        Initialize Cloud Agent
        Roman Urdu: Cloud Agent ko initialize karna
        """
        self.vault_path = Path(VAULT_PATH)
        self.cloud_domain = self.vault_path / CLOUD_DOMAIN
        self.in_progress = self.vault_path / "In_Progress"
        
        # Roman Urdu: Ensure cloud domain directory exists
        self._ensure_domain_exists()
        
        logger.info(f"Cloud Agent initialized. Domain: {CLOUD_DOMAIN}")

    def _ensure_domain_exists(self):
        """
        Ensure cloud domain directory exists
        Roman Urdu: Cloud domain directory ko ensure karna
        """
        if not self.cloud_domain.exists():
            self.cloud_domain.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created cloud domain directory: {CLOUD_DOMAIN}")
        
        if not self.in_progress.exists():
            self.in_progress.mkdir(parents=True, exist_ok=True)
            logger.info("Created In_Progress directory")

    def claim_task(self, filename):
        """
        Claim a task by moving it from cloud domain to In_Progress
        Roman Urdu: Task ko claim karna by moving to In_Progress
        
        Args:
            filename (str): Name of the task file to claim
            
        Returns:
            bool: True if successful, False otherwise
        """
        source = self.cloud_domain / filename
        dest = self.in_progress / filename
        
        if not source.exists():
            logger.error(f"Task not found in cloud domain: {filename}")
            return False
        
        try:
            # Roman Urdu: File ko In_Progress mein move karna
            success = move_file(str(source), str(dest))
            if success:
                logger.info(f"Claimed task: {filename} -> In_Progress")
                # Roman Urdu: Claim metadata add karna
                self._add_claim_metadata(dest, "cloud")
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

    def email_triage(self, email_data):
        """
        Triage incoming emails and categorize them
        Roman Urdu: Incoming emails ko categorize karna
        
        Args:
            email_data (dict): Email data with subject, sender, body, etc.
            
        Returns:
            dict: Triage result with priority, category, action
        """
        # Roman Urdu: Email ko analyze karna aur priority decide karna
        subject = email_data.get("subject", "").lower()
        sender = email_data.get("sender", "")
        body = email_data.get("body", "").lower()
        
        # Roman Urdu: Priority rules
        urgent_keywords = ["urgent", "asap", "emergency", "critical", "immediate"]
        important_keywords = ["meeting", "deadline", "payment", "invoice", "contract"]
        
        priority = "normal"
        category = "general"
        action = "review"
        
        # Roman Urdu: Urgent keywords check
        for keyword in urgent_keywords:
            if keyword in subject or keyword in body:
                priority = "urgent"
                action = "reply_immediately"
                break
        
        # Roman Urdu: Important keywords check
        if priority != "urgent":
            for keyword in important_keywords:
                if keyword in subject or keyword in body:
                    priority = "high"
                    action = "reply_today"
                    break
        
        # Roman Urdu: Category classification
        if any(word in subject for word in ["meeting", "schedule", "calendar"]):
            category = "meeting"
        elif any(word in subject for word in ["invoice", "payment", "bill"]):
            category = "finance"
            action = "forward_to_local"  # Roman Urdu: Finance tasks local agent ko
        elif any(word in subject for word in ["social", "post", "content"]):
            category = "social_media"
        elif any(word in subject for word in ["reply", "response", "inquiry"]):
            category = "reply_needed"
        
        result = {
            "priority": priority,
            "category": category,
            "action": action,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"Email triaged: {email_data.get('subject', 'N/A')} -> {priority}/{category}")
        return result

    def create_email_task(self, email_data, triage_result):
        """
        Create a task file for email in cloud domain
        Roman Urdu: Email ke liye task file banana
        
        Args:
            email_data (dict): Original email data
            triage_result (dict): Result from email_triage()
            
        Returns:
            str: Filename of created task, or None if failed
        """
        # Roman Urdu: Unique filename generate karna
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        subject_slug = email_data.get("subject", "no_subject")[:30].replace(" ", "_").replace("/", "_")
        filename = f"email_{timestamp}_{subject_slug}.md"
        
        # Roman Urdu: Markdown task file content
        content = f"""---
type: email_task
domain: cloud
priority: {triage_result['priority']}
category: {triage_result['category']}
action: {triage_result['action']}
created_at: {triage_result['timestamp']}
sender: {email_data.get('sender', 'unknown')}
subject: {email_data.get('subject', 'No Subject')}
status: pending
---

# Email Task

## Original Email
- **From:** {email_data.get('sender', 'Unknown')}
- **Subject:** {email_data.get('subject', 'No Subject')}
- **Received:** {triage_result['timestamp']}

## Body
{email_data.get('body', 'No content')}

## Triage Result
- **Priority:** {triage_result['priority']}
- **Category:** {triage_result['category']}
- **Action:** {triage_result['action']}

## Draft Reply
<!-- Cloud Agent: Draft reply yahan likhen -->

"""
        
        file_path = self.cloud_domain / filename
        success = write_file(str(file_path), content)
        
        if success:
            logger.info(f"Created email task: {filename}")
            return filename
        else:
            logger.error(f"Failed to create email task: {filename}")
            return None

    def draft_reply(self, email_task_filename, reply_content):
        """
        Draft a reply for an email task
        Roman Urdu: Email ka reply draft karna
        
        Args:
            email_task_filename (str): Name of the email task file
            reply_content (str): Draft reply content
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = self.cloud_domain / email_task_filename
        
        # Roman Urdu: Agar file In_Progress mein hai to wahan se read karna
        if not file_path.exists():
            file_path = self.in_progress / email_task_filename
        
        if not file_path.exists():
            logger.error(f"Email task not found: {email_task_filename}")
            return False
        
        try:
            content = read_file(str(file_path))
            
            # Roman Urdu: Draft Reply section ko update karna
            if "## Draft Reply" in content:
                # Roman Urdu: Existing draft ko replace karna
                parts = content.split("## Draft Reply")
                updated_content = parts[0] + f"## Draft Reply\n\n{reply_content}\n"
            else:
                # Roman Urdu: Naya Draft Reply section add karna
                updated_content = content + f"\n## Draft Reply\n\n{reply_content}\n"
            
            # Roman Urdu: Status update karna
            updated_content = updated_content.replace("status: pending", "status: draft_ready")
            
            success = write_file(str(file_path), updated_content)
            if success:
                logger.info(f"Draft reply added to: {email_task_filename}")
            return success
        except Exception as e:
            logger.error(f"Error drafting reply: {str(e)}")
            return False

    def create_social_post_draft(self, post_data):
        """
        Create a social media post draft
        Roman Urdu: Social media post draft banana
        
        Args:
            post_data (dict): Post data with platform, topic, key_points
            
        Returns:
            str: Filename of created draft, or None if failed
        """
        # Roman Urdu: Unique filename generate karna
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        platform = post_data.get("platform", "generic")
        topic_slug = post_data.get("topic", "post")[:30].replace(" ", "_")
        filename = f"social_{platform}_{timestamp}_{topic_slug}.md"
        
        # Roman Urdu: Post content generate karna
        platforms_config = {
            "twitter": {"char_limit": 280, "hashtags": True},
            "linkedin": {"char_limit": 3000, "hashtags": True},
            "facebook": {"char_limit": 63206, "hashtags": False},
            "instagram": {"char_limit": 2200, "hashtags": True}
        }
        
        config = platforms_config.get(platform.lower(), {"char_limit": 280, "hashtags": True})
        
        # Roman Urdu: Draft content create karna
        content = f"""---
type: social_post_draft
domain: cloud
platform: {platform}
topic: {post_data.get('topic', 'General')}
created_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
status: draft
char_limit: {config['char_limit']}
---

# Social Media Post Draft

## Platform: {platform.capitalize()}
## Topic: {post_data.get('topic', 'General')}

## Key Points
{chr(10).join(f"- {point}" for point in post_data.get('key_points', []))}

## Draft Content
<!-- Cloud Agent: Yahan post content likhen -->

"""
        
        if config['hashtags']:
            content += "\n## Suggested Hashtags\n#AI #Automation #Productivity\n"
        
        content += f"""
## Notes
- Character limit: {config['char_limit']}
- Created by: Cloud Agent
- Needs approval from Local Agent before posting

"""
        
        file_path = self.cloud_domain / filename
        success = write_file(str(file_path), content)
        
        if success:
            logger.info(f"Created social post draft: {filename}")
            return filename
        else:
            logger.error(f"Failed to create social post draft: {filename}")
            return None

    def list_pending_tasks(self):
        """
        List all pending tasks in cloud domain
        Roman Urdu: Cloud domain mein pending tasks ki list
        
        Returns:
            list: List of pending task filenames
        """
        tasks = []
        if self.cloud_domain.exists():
            files = list_folder(str(self.cloud_domain))
            for file in files:
                if file.endswith(".md"):
                    tasks.append(file)
        
        logger.info(f"Found {len(tasks)} pending tasks in cloud domain")
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
        file_path = self.cloud_domain / filename
        
        if not file_path.exists():
            file_path = self.in_progress / filename
        
        if not file_path.exists():
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
                "location": "cloud_domain" if file_path.parent.name == "cloud" else "in_progress"
            }
        except Exception as e:
            logger.error(f"Error reading task status: {str(e)}")
            return None

    def process_incoming_email(self, email_data):
        """
        Full pipeline: Triage email -> Create task -> Draft reply if needed
        Roman Urdu: Complete email processing pipeline
        
        Args:
            email_data (dict): Email data
            
        Returns:
            str: Created task filename, or None if failed
        """
        # Roman Urdu: Step 1: Triage
        triage_result = self.email_triage(email_data)
        logger.info(f"Email triaged: {triage_result}")
        
        # Roman Urdu: Step 2: Create task
        task_filename = self.create_email_task(email_data, triage_result)
        
        if not task_filename:
            return None
        
        # Roman Urdu: Step 3: Auto-draft reply if category is reply_needed
        if triage_result['category'] == 'reply_needed':
            # Roman Urdu: Simple acknowledgment draft
            draft_reply = f"""Dear Sender,

Thank you for your email regarding "{email_data.get('subject', 'your inquiry')}".

This is an automated acknowledgment. Our team will review your message and respond within 24 hours.

Best regards,
AI Employee System
"""
            self.draft_reply(task_filename, draft_reply)
        
        return task_filename


def main():
    """
    Main function to demonstrate Cloud Agent capabilities
    Roman Urdu: Cloud Agent capabilities ko demonstrate karna
    """
    print("=" * 60)
    print("Cloud Agent - Platinum Tier")
    print("Domain: /Needs_Action/cloud/")
    print("=" * 60)
    
    # Initialize agent
    agent = CloudAgent()
    
    # Demo: Email triage
    print("\n[Demo] Email Triage:")
    demo_email = {
        "sender": "client @example.com",
        "subject": "Urgent: Meeting Schedule for Project Review",
        "body": "Hi, we need to schedule an urgent meeting to review the project progress. Please let me know your availability."
    }
    triage_result = agent.email_triage(demo_email)
    print(f"  Priority: {triage_result['priority']}")
    print(f"  Category: {triage_result['category']}")
    print(f"  Action: {triage_result['action']}")
    
    # Demo: Create email task
    print("\n[Demo] Creating Email Task:")
    task_file = agent.create_email_task(demo_email, triage_result)
    print(f"  Created: {task_file}")
    
    # Demo: List pending tasks
    print("\n[Demo] Pending Tasks in Cloud Domain:")
    tasks = agent.list_pending_tasks()
    for task in tasks:
        print(f"  - {task}")
    
    # Demo: Social post draft
    print("\n[Demo] Creating Social Post Draft:")
    post_data = {
        "platform": "linkedin",
        "topic": "AI Automation",
        "key_points": [
            "AI agents are transforming business workflows",
            "Automation reduces manual work by 80%",
            "Future of work is human-AI collaboration"
        ]
    }
    social_file = agent.create_social_post_draft(post_data)
    print(f"  Created: {social_file}")
    
    print("\n" + "=" * 60)
    print("Cloud Agent demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
