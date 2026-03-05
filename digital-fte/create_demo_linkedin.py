#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Demo LinkedIn Messages - For Hackathon Demo

Yeh script demo LinkedIn messages/posts create karti hai jo safe hain
public GitHub ke liye. Koi real profile ya connection data nahi.
"""

import os
from datetime import datetime

# Configuration
VAULT_BASE = r"D:\AI_Workspace_bronze_silver_gold_platinum\AI_Employee_Vault"
INBOX_DIR = os.path.join(VAULT_BASE, "Inbox")
PENDING_POSTS_DIR = os.path.join(VAULT_BASE, "Pending_Posts")

# Demo LinkedIn Messages (Fake Data - Safe for GitHub)
DEMO_LINKEDIN_MESSAGES = [
    {
        "filename": "LinkedIn_20260227_110000_Recruiter_Demo.md",
        "sender": "Sarah Johnson - Recruiter Demo",
        "profile": "linkedin.com/in/recruiter-demo",
        "timestamp": "2026-02-27 11:00:00",
        "type": "connection_request",
        "message": """Hi! I came across your profile and was impressed by your AI projects. I'd love to connect and discuss some exciting opportunities at Tech Corp. Would you be open to a quick chat?""",
    },
    {
        "filename": "LinkedIn_20260227_150000_Client_Demo.md",
        "sender": "Michael Chen - CEO Demo Company",
        "profile": "linkedin.com/in/ceo-demo",
        "timestamp": "2026-02-27 15:00:00",
        "type": "business_inquiry",
        "message": """Hello! Our company is looking for an AI automation solution. Your AI Employee System looks perfect for our needs. Can we schedule a demo call next week? Budget: $50K-100K.""",
    },
    {
        "filename": "LinkedIn_20260226_093000_Partner_Demo.md",
        "sender": "Emily Rodriguez - Partnership Demo",
        "profile": "linkedin.com/in/partnership-demo",
        "timestamp": "2026-02-26 09:30:00",
        "type": "partnership",
        "message": """Hi there! I represent a venture capital firm interested in AI startups. We'd love to explore potential investment opportunities. Are you available for a call this week?""",
    },
]

# Demo LinkedIn Posts (Fake Content - Safe for GitHub)
DEMO_LINKEDIN_POSTS = [
    {
        "filename": "LinkedIn_Post_Demo_1.md",
        "topic": "AI Employee System Launch",
        "date": "2026-02-27",
        "status": "draft",
        "content": """🚀 Exciting News! AI Employee System is Here!

I'm thrilled to announce the launch of my latest project - the AI Employee System!

This innovative solution helps businesses automate:
✅ Email management & prioritization
✅ Social media posting (LinkedIn, Facebook)
✅ WhatsApp message monitoring
✅ Task scheduling & reminders
✅ Real-time dashboard updates

Key Features:
- Multi-platform integration
- Smart keyword detection
- Automated responses
- Comprehensive audit logging

Perfect for small businesses and solopreneurs looking to scale efficiently!

#AI #Automation #Productivity #Innovation #TechStartup #ArtificialIntelligence

---
*This is a DEMO post for hackathon purposes*
""",
    },
    {
        "filename": "LinkedIn_Post_Demo_2.md",
        "topic": "Hackathon Project Showcase",
        "date": "2026-02-27",
        "status": "draft",
        "content": """💡 Hackathon Project: AI Employee System

Proud to showcase my hackathon project - an AI-powered employee automation system!

🏆 What it does:
- Monitors emails & WhatsApp for urgent messages
- Auto-posts to LinkedIn & Facebook
- Creates real-time dashboards
- Maintains audit logs for compliance

🛠️ Tech Stack:
- Python
- Google Gmail API
- Meta Business API
- Playwright for web automation
- Obsidian for knowledge management

🎯 Impact:
- Saves 10+ hours per week
- Never miss urgent messages
- Consistent social media presence

Open to feedback and collaboration!

#Hackathon #AI #Python #Automation #Developer #Innovation

---
*This is a DEMO post for hackathon purposes*
""",
    },
    {
        "filename": "LinkedIn_Post_Demo_3.md",
        "topic": "Learning Journey Share",
        "date": "2026-02-26",
        "status": "draft",
        "content": """📚 My AI Learning Journey - 6 Month Update

6 months ago, I started learning AI automation. Here's what I've built:

🎯 Projects Completed:
1. Gmail Watcher - Auto-process emails
2. WhatsApp Monitor - Track urgent messages
3. Social Media Auto-Poster
4. AI Dashboard System
5. Voice Assistant Integration

💪 Key Learnings:
- API integrations are powerful
- Error handling is crucial
- User experience matters
- Documentation is key

🚀 What's Next:
- Advanced NLP for message classification
- Voice commands integration
- Mobile app development

To everyone starting their AI journey: Keep building, keep learning!

#LearningJourney #AI #CareerGrowth #TechCommunity #Developer

---
*This is a DEMO post for hackathon purposes*
""",
    },
]


def create_demo_linkedin_messages():
    """Create demo LinkedIn message files"""
    
    # Create inbox directory
    os.makedirs(INBOX_DIR, exist_ok=True)
    
    print("=" * 60)
    print("Creating Demo LinkedIn Messages")
    print("=" * 60)
    print(f"Folder: {INBOX_DIR}")
    print()
    
    created_count = 0
    
    for demo in DEMO_LINKEDIN_MESSAGES:
        filepath = os.path.join(INBOX_DIR, demo["filename"])
        
        # Create markdown content
        content = f"""---
type: linkedin_message
priority: normal
sender: {demo['sender']}
profile: {demo['profile']}
received_at: {demo['timestamp']}
message_type: {demo['type']}
status: new
---

# LinkedIn Message

## Sender Information
- **Name:** {demo['sender']}
- **Profile:** {demo['profile']}
- **Received:** {demo['timestamp']}
- **Type:** {demo['type'].replace('_', ' ').title()}

## Message Content
{demo['message']}

## Suggested Response
<!-- Yahan response draft likhen -->

## Action Required
<!-- Follow-up action likhen -->

---
*This is a DEMO LinkedIn message for hackathon testing purposes*
*No real profiles or personal data included*
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Created: {demo['filename']}")
            print(f"  Sender: {demo['sender']}")
            print(f"  Type: {demo['type'].replace('_', ' ').title()}")
            created_count += 1
        except Exception as e:
            print(f"[ERROR] Creating {demo['filename']}: {e}")
    
    print()
    print(f"Total demo LinkedIn messages created: {created_count}")
    return created_count


def create_demo_linkedin_posts():
    """Create demo LinkedIn post drafts"""
    
    # Create pending posts directory
    os.makedirs(PENDING_POSTS_DIR, exist_ok=True)
    
    print()
    print("=" * 60)
    print("Creating Demo LinkedIn Post Drafts")
    print("=" * 60)
    print(f"Folder: {PENDING_POSTS_DIR}")
    print()
    
    created_count = 0
    
    for demo in DEMO_LINKEDIN_POSTS:
        filepath = os.path.join(PENDING_POSTS_DIR, demo["filename"])
        
        # Create markdown content
        content = f"""---
type: linkedin_post
topic: {demo['topic']}
scheduled_date: {demo['date']}
status: {demo['status']}
platform: LinkedIn
created_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---

# LinkedIn Post Draft

## Post Information
- **Topic:** {demo['topic']}
- **Scheduled:** {demo['date']}
- **Status:** {demo['status'].title()}
- **Platform:** LinkedIn

## Content

{demo['content']}

## Posting Checklist
- [ ] Review content for errors
- [ ] Add relevant image/media
- [ ] Check hashtags
- [ ] Schedule optimal posting time
- [ ] Get approval (if needed)

## Performance Tracking
<!-- Post ke metrics yahan track karein -->
- Impressions: _
- Likes: _
- Comments: _
- Shares: _

---
*This is a DEMO LinkedIn post for hackathon testing purposes*
"""

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Created: {demo['filename']}")
            print(f"  Topic: {demo['topic']}")
            created_count += 1
        except Exception as e:
            print(f"[ERROR] Creating {demo['filename']}: {e}")
    
    print()
    print(f"Total demo LinkedIn posts created: {created_count}")
    return created_count


def main():
    """Main function to create all demo LinkedIn content"""
    
    print()
    print("+" + "=" * 60 + "+")
    print("|     Creating Demo LinkedIn Content for Hackathon       |")
    print("+" + "=" * 60 + "+")
    print()
    
    # Create demo messages
    messages_created = create_demo_linkedin_messages()
    
    # Create demo posts
    posts_created = create_demo_linkedin_posts()
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"LinkedIn Messages Created: {messages_created}")
    print(f"LinkedIn Posts Created:    {posts_created}")
    print("=" * 60)
    print()
    print("[SUCCESS] Demo LinkedIn content is ready for hackathon!")
    print()
    print("Locations:")
    print(f"  Messages: {os.path.join(INBOX_DIR)}")
    print(f"  Posts:    {PENDING_POSTS_DIR}")
    print()
    print("Next steps:")
    print("1. Review demo content in AI_Employee_Vault/")
    print("2. Show in hackathon presentation")
    print("3. Explain AI Employee's LinkedIn automation")
    print()


if __name__ == "__main__":
    main()
