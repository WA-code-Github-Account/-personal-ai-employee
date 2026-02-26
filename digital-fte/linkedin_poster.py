#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Poster - Professional Social Media Automation
LinkedIn par professional posts automate karne wala module

═══════════════════════════════════════════════════════════════════════════════
📘 HOW TO GET LINKEDIN API CREDENTIALS
═══════════════════════════════════════════════════════════════════════════════

Step 1: Create LinkedIn Developer Account
─────────────────────────────────────────
URL: https://www.linkedin.com/developers/

1. LinkedIn pe login karein
2. Developers page pe jayein
3. "Create app" button click karein

Step 2: Create LinkedIn App
─────────────────────────────────────────
1. App name dein (e.g., "AI Employee System")
2. Company select karein (ya personal brand)
3. App logo upload karein (optional)
4. Privacy policy URL (optional for testing)

Step 3: Get API Credentials
─────────────────────────────────────────
App create hone ke baad:

1. "Auth" tab pe jayein
2. Note down ye values:
   - Client ID
   - Client Secret
   - Redirect URL (default: https://www.linkedin.com/oauth/v2/authorization)

Step 4: Request Permissions
─────────────────────────────────────────
Required permissions:
✓ w_member_social - Post updates on behalf of members
✓ r_basicprofile  - Read basic profile information
✓ r_emailaddress  - Read email address

Permission request process:
1. "Auth" tab mein "Request permission" click karein
2. Permission select karein
3. Use case describe karein
4. Submit for review (2-3 days approval)

Step 5: Generate Access Token (Testing)
─────────────────────────────────────────
For testing without full OAuth flow:

Option A: LinkedIn API Explorer
1. https://www.linkedin.com/developers/tools/oauth/access-token-generator
2. App select karein
3. Permissions select karein (w_member_social, r_basicprofile)
4. "Generate access token" click karein
5. Token copy karein (expires in 60 days)

Option B: Manual OAuth Flow
1. Browser mein ye URL open karein:
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URL&scope=w_member_social%20r_basicprofile

2. Authorize app
3. Redirect URL pe authorization code milega
4. Exchange code for token:
   POST https://www.linkedin.com/oauth/v2/accessToken
   - client_id=YOUR_CLIENT_ID
   - client_secret=YOUR_CLIENT_SECRET
   - code=AUTHORIZATION_CODE
   - redirect_uri=YOUR_REDIRECT_URL
   - grant_type=authorization_code

Step 6: Add to .env File
─────────────────────────────────────────
Open .env file in digital-fte/ folder and add:

    LINKEDIN_ACCESS_TOKEN=AQXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    LINKEDIN_CLIENT_ID=XXXXXXXXXXXX
    LINKEDIN_CLIENT_SECRET=XXXXXXXXXXXXXXXX

Step 7: Test Your Token
─────────────────────────────────────────
Run: python test_linkedin.py

Ye script verify karegi ke token valid hai aur profile info display karegi.

═══════════════════════════════════════════════════════════════════════════════
⚠️ IMPORTANT NOTES
═══════════════════════════════════════════════════════════════════════════════

• Token Expiry: Access tokens expire in 60 days. Refresh token use karein
  for long-term access.

• Rate Limits: LinkedIn API has rate limits:
  - 500 requests per day per user
  - Don't post more than 5 times per day

• Content Guidelines:
  - Professional content only
  - No spam or promotional content
  - Follow LinkedIn's User Agreement

• Security: NEVER commit your .env file to Git! It's already in .gitignore.

• API Version: Currently using v2. LinkedIn may deprecate older versions.

• Approval Process: Some permissions require LinkedIn approval (2-3 days).

═══════════════════════════════════════════════════════════════════════════════
🔗 USEFUL LINKS
═══════════════════════════════════════════════════════════════════════════════

• LinkedIn Developers: https://www.linkedin.com/developers/
• API Documentation: https://learn.microsoft.com/en-us/linkedin/
• Access Token Generator: https://www.linkedin.com/developers/tools/oauth/access-token-generator
• API Explorer: https://www.linkedin.com/developers/tools/explorer
• Share API: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin
• Rate Limits: https://learn.microsoft.com/en-us/linkedin/consumer/get-access#rate-limiting

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv

# Roman Urdu: Audit logger aur error recovery ko import karna
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_logger import log_task_start, log_task_complete, log_file_operation, log_error
from error_recovery import retry_with_backoff, safe_execute, get_recovery_strategy

# Roman Urdu: Environment variables load karna
load_dotenv()

# Roman Urdu: Configuration aur global variables
VAULT_BASE = "D:/AI_Workspace_bronze_silver_gold_platinum/AI_Employee_Vault"
PENDING_POSTS_DIR = os.path.join(VAULT_BASE, "Pending_Posts")
DASHBOARD_PATH = os.path.join(VAULT_BASE, "Dashboard.md")

# Roman Urdu: LinkedIn API configuration
LINKEDIN_API_VERSION = "202402"
LINKEDIN_API_BASE_URL = "https://api.linkedin.com/v2"
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# Roman Urdu: Logging setup
LOG_FILE = "linkedin_poster.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LinkedInPoster:
    """
    LinkedIn Poster for AI Employee System
    LinkedIn par professional posts create karne wala class
    """

    def __init__(self, access_token: str = None, client_id: str = None,
                 client_secret: str = None, test_mode: bool = False):
        """
        Initialize LinkedIn Poster
        LinkedIn Poster ko initialize karna

        Args:
            access_token: LinkedIn OAuth access token
            client_id: LinkedIn app client ID
            client_secret: LinkedIn app client secret
            test_mode: If True, save drafts without posting
        """
        # Roman Urdu: Configuration se credentials lena
        self.access_token = access_token or os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        self.client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET", "")
        self.test_mode = test_mode

        # Roman Urdu: Pending posts directory ensure karna
        os.makedirs(PENDING_POSTS_DIR, exist_ok=True)

        # Roman Urdu: Initialization log
        if self.test_mode:
            logger.info("LinkedIn Poster initialized in TEST MODE")
            logger.info("Posts will be saved as drafts, not published")
        else:
            logger.info(f"LinkedIn Poster initialized (Client ID: {self.client_id[:8]}...)")

        # Roman Urdu: Audit log
        log_task_start("LinkedIn Poster Init", source="linkedin_poster",
                      test_mode=str(test_mode))

    def is_configured(self) -> bool:
        """
        Check if LinkedIn credentials are configured
        Check karo ke LinkedIn credentials configure hain ya nahi

        Returns:
            bool: True if access token is available
        """
        # Roman Urdu: Token check karna
        has_token = bool(self.access_token and self.access_token.strip())

        if not has_token:
            logger.warning("LINKEDIN_ACCESS_TOKEN not configured")
            logger.info("Token generate karne ke liye test_linkedin.py run karein")

        return has_token

    def get_profile_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current user's LinkedIn profile information
        Current user ki LinkedIn profile information lena

        Returns:
            dict: Profile information or None if error
        """
        # Roman Urdu: API endpoint
        endpoint = f"{LINKEDIN_API_BASE_URL}/me"

        # Roman Urdu: Request headers
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        try:
            # Roman Urdu: API call
            response = requests.get(endpoint, headers=headers, timeout=10)
            response.raise_for_status()
            profile_data = response.json()

            logger.info(f"Profile retrieved: {profile_data.get('id', 'Unknown')}")
            return profile_data

        except requests.exceptions.RequestException as e:
            error_msg = f"Profile fetch error: {str(e)}"
            logger.error(error_msg)
            log_error("LINKEDIN_PROFILE_ERROR", str(e),
                     action="get_profile_info", source="linkedin_poster")
            return None

    def read_dashboard_content(self) -> Optional[str]:
        """
        Read content from Dashboard.md
        Dashboard.md se content parhna

        Returns:
            str: Dashboard content or None if error
        """
        # Roman Urdu: Audit log for file read
        log_file_operation("READ", DASHBOARD_PATH, source="linkedin_poster")

        try:
            if not os.path.exists(DASHBOARD_PATH):
                logger.warning(f"Dashboard.md not found: {DASHBOARD_PATH}")
                return None

            with open(DASHBOARD_PATH, 'r', encoding='utf-8') as f:
                content = f.read()

            # Roman Urdu: Audit log for successful read
            log_file_operation("READ", DASHBOARD_PATH, result="SUCCESS",
                              file_size=len(content), source="linkedin_poster")

            logger.info(f"Read Dashboard.md ({len(content)} characters)")
            return content

        except Exception as e:
            logger.error(f"Error reading Dashboard.md: {str(e)}")
            log_error("DASHBOARD_READ_ERROR", str(e),
                     file_involved=DASHBOARD_PATH, action="read_dashboard_content")
            return None

    def format_linkedin_post(self, content: str, custom_message: str = None) -> str:
        """
        Format content for professional LinkedIn post
        Content ko professional LinkedIn post ke liye format karna

        Args:
            content: Raw content to format
            custom_message: Optional custom message to prepend

        Returns:
            str: Formatted LinkedIn post content
        """
        # Roman Urdu: Post formatting shuru karna
        logger.info("Formatting content for LinkedIn post")

        # Roman Urdu: Timestamp add karna
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Roman Urdu: Custom message ya default header
        if custom_message:
            header = custom_message
        else:
            header = "🤖 AI Employee System Update"

        # Roman Urdu: Content ko clean karna (remove markdown headers)
        clean_content = content
        for i in range(6, 0, -1):
            clean_content = clean_content.replace('#' * i + ' ', '')

        # Roman Urdu: LinkedIn ke liye optimize karna
        # Line breaks add karna for readability
        lines = clean_content.split('\n')
        formatted_lines = []

        for line in lines:
            # Roman Urdu: Empty lines skip karna
            if line.strip():
                formatted_lines.append(line)

        # Roman Urdu: Join with proper spacing
        clean_content = '\n\n'.join(formatted_lines[:10])  # LinkedIn limit

        # Roman Urdu: Hashtags add karna
        hashtags = "#AIEmployee #Automation #Productivity #TechInnovation #LinkedInAutomation"

        # Roman Urdu: Final formatted post
        formatted_post = f"""{header}

{clean_content}

---
📅 Posted: {timestamp}
🔧 AI Employee System - Platinum Tier

{hashtags}"""

        # Roman Urdu: Character count check (LinkedIn limit: 3000)
        if len(formatted_post) > 3000:
            logger.warning(f"Post too long ({len(formatted_post)} chars), truncating...")
            formatted_post = formatted_post[:2900] + "\n\n... (truncated)"

        logger.info(f"Formatted post ({len(formatted_post)} characters)")
        return formatted_post

    def create_post_draft(self, content: str, message: str = None) -> str:
        """
        Create a post draft file
        Post draft file banana

        Args:
            content: Post content
            message: Optional custom message

        Returns:
            str: Path to draft file
        """
        # Roman Urdu: Draft file ka naam aur path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_filename = f"LinkedIn_Draft_{timestamp}.md"
        draft_path = os.path.join(PENDING_POSTS_DIR, draft_filename)

        # Roman Urdu: Draft content create karna
        draft_content = f"""# LinkedIn Post Draft

## Status: Pending Review

## Post Details
- **Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Platform:** LinkedIn
- **Test Mode:** {self.test_mode}

## Content
{content}

## Custom Message
{message if message else "*Using default message*"}

## Action Required
Review this draft and either:
1. Change status to "Approved" to enable posting
2. Change status to "Rejected" to discard
3. Edit content and save

---
*Generated by AI Employee LinkedIn Poster*
"""

        # Roman Urdu: Draft file save karna
        try:
            with open(draft_path, 'w', encoding='utf-8') as f:
                f.write(draft_content)

            # Roman Urdu: Audit log
            log_file_operation("WRITE", draft_path, result="SUCCESS",
                              file_size=len(draft_content), source="linkedin_poster")

            logger.info(f"Draft saved: {draft_path}")
            return draft_path

        except Exception as e:
            logger.error(f"Error saving draft: {str(e)}")
            log_error("DRAFT_SAVE_ERROR", str(e),
                     file_involved=draft_path, action="create_post_draft")
            raise

    @retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
    def post_to_linkedin_api(self, content: str) -> Dict[str, Any]:
        """
        Post to LinkedIn using API v2
        LinkedIn API v2 se post karna

        Args:
            content: Formatted post content

        Returns:
            dict: LinkedIn API response
        """
        # Roman Urdu: API endpoint - Share API
        endpoint = f"{LINKEDIN_API_BASE_URL}/shares"

        # Roman Urdu: Get person URN (required for posting)
        person_urn = self._get_person_urn()

        if not person_urn:
            return {
                'success': False,
                'error': 'Could not get person URN'
            }

        # Roman Urdu: Request headers
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json',
            'linkedin-version': LINKEDIN_API_VERSION
        }

        # Roman Urdu: Request body - LinkedIn Share API format
        payload = {
            "owner": person_urn,
            "subject": "AI Employee System Update",
            "text": {
                "text": content
            },
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "visibility": "PUBLIC"
        }

        # Roman Urdu: API call log
        logger.info(f"Posting to LinkedIn (Owner: {person_urn})")
        log_task_start("LinkedIn API Post", source="linkedin_poster")

        try:
            # Roman Urdu: POST request bhejna
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)

            # Roman Urdu: Response check karna
            response.raise_for_status()
            result = response.json()

            # Roman Urdu: Success log
            logger.info(f"LinkedIn post successful: {result}")
            log_task_complete("LinkedIn API Post", result="SUCCESS",
                             source="linkedin_poster")

            return {
                'success': True,
                'post_id': result.get('id'),
                'post_urn': result.get('share'),
                'response': result
            }

        except requests.exceptions.HTTPError as e:
            # Roman Urdu: HTTP error handle karna
            error_msg = f"LinkedIn API HTTP Error: {str(e)}"
            logger.error(error_msg)

            # Roman Urdu: Error response parse karna
            try:
                error_response = e.response.json()
                error_details = error_response.get('message', str(e))
            except:
                error_details = str(e)

            log_error("LINKEDIN_HTTP_ERROR", error_details,
                     action="post_to_linkedin_api", source="linkedin_poster")

            return {
                'success': False,
                'error': error_details,
                'status_code': e.response.status_code
            }

        except requests.exceptions.RequestException as e:
            # Roman Urdu: Network error handle karna
            error_msg = f"Network error: {str(e)}"
            logger.error(error_msg)
            log_error("LINKEDIN_NETWORK_ERROR", str(e),
                     action="post_to_linkedin_api", source="linkedin_poster")
            return {
                'success': False,
                'error': error_msg
            }

    def _get_person_urn(self) -> Optional[str]:
        """
        Get LinkedIn person URN (required for posting)
        LinkedIn person URN lena (posting ke liye zaroori)

        Returns:
            str: Person URN (e.g., "urn:li:person:XXXXXXXXXX")
        """
        # Roman Urdu: API endpoint
        endpoint = f"{LINKEDIN_API_BASE_URL}/me"

        # Roman Urdu: Request headers
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        try:
            # Roman Urdu: API call
            response = requests.get(endpoint, headers=headers, timeout=10)
            response.raise_for_status()
            profile_data = response.json()

            # Roman Urdu: URN extract karna
            person_id = profile_data.get('id')
            if person_id:
                person_urn = f"urn:li:person:{person_id}"
                logger.info(f"Person URN: {person_urn}")
                return person_urn
            else:
                logger.error("Person ID not found in profile")
                return None

        except Exception as e:
            logger.error(f"Error getting person URN: {str(e)}")
            return None

    def post_to_linkedin(self, content: str = None, custom_message: str = None,
                        read_from_dashboard: bool = True) -> Dict[str, Any]:
        """
        Main function to post to LinkedIn
        LinkedIn par post karne ka main function

        Args:
            content: Custom content (overrides dashboard if provided)
            custom_message: Optional custom message
            read_from_dashboard: If True, read content from Dashboard.md

        Returns:
            dict: Result with success status and post/draft info
        """
        # Roman Urdu: Post operation start karna
        logger.info("=" * 60)
        logger.info("LinkedIn Post Operation Started")
        logger.info("=" * 60)

        log_task_start("LinkedIn Post", source="linkedin_poster",
                      test_mode=str(self.test_mode))

        # Roman Urdu: Step 1: Content obtain karna
        if content is None and read_from_dashboard:
            logger.info("Reading content from Dashboard.md...")
            dashboard_content = self.read_dashboard_content()

            if dashboard_content:
                content = dashboard_content
            else:
                content = "AI Employee System - System Update\n\nNo dashboard content available."
                logger.warning("Using default content (Dashboard not available)")

        # Roman Urdu: Step 2: Content format karna
        formatted_content = self.format_linkedin_post(content, custom_message)

        # Roman Urdu: Step 3: Test mode check
        if self.test_mode or not self.is_configured():
            logger.info("Test mode or not configured - saving as draft")

            # Roman Urdu: Draft save karna
            draft_path = self.create_post_draft(formatted_content, custom_message)

            result = {
                'success': True,
                'mode': 'draft',
                'draft_path': draft_path,
                'message': 'Post saved as draft (test mode or not configured)',
                'content_preview': formatted_content[:200] + '...' if len(formatted_content) > 200 else formatted_content
            }

            logger.info(f"Draft created: {draft_path}")
            log_task_complete("LinkedIn Post", result="DRAFT_SAVED",
                             source="linkedin_poster")

            return result

        # Roman Urdu: Step 4: Actual LinkedIn post
        logger.info("Posting to LinkedIn...")
        api_result = self.post_to_linkedin_api(formatted_content)

        if api_result['success']:
            # Roman Urdu: Post confirmation
            result = {
                'success': True,
                'mode': 'published',
                'post_id': api_result['post_id'],
                'post_urn': api_result['post_urn'],
                'post_url': f"https://www.linkedin.com/feed/update/{api_result['post_urn']}",
                'message': 'Post published successfully',
                'content_preview': formatted_content[:200] + '...' if len(formatted_content) > 200 else formatted_content
            }

            logger.info(f"Post published: {api_result['post_id']}")
            log_task_complete("LinkedIn Post", result="PUBLISHED",
                             source="linkedin_poster")
        else:
            # Roman Urdu: Post failed - save as draft
            logger.warning("Post failed - saving as draft")
            draft_path = self.create_post_draft(formatted_content, custom_message)

            result = {
                'success': False,
                'mode': 'failed_to_draft',
                'draft_path': draft_path,
                'error': api_result.get('error', 'Unknown error'),
                'message': 'Post failed, saved as draft',
                'content_preview': formatted_content[:200] + '...' if len(formatted_content) > 200 else formatted_content
            }

            log_task_complete("LinkedIn Post", result="FAILED",
                             error=api_result.get('error', 'Unknown'),
                             source="linkedin_poster")

        logger.info("=" * 60)
        logger.info("LinkedIn Post Operation Complete")
        logger.info("=" * 60)

        return result

    def list_pending_posts(self) -> list:
        """
        List all pending post drafts
        Saare pending post drafts ko list karna

        Returns:
            list: List of draft file paths
        """
        # Roman Urdu: Pending posts directory scan karna
        try:
            drafts = []
            for file in os.listdir(PENDING_POSTS_DIR):
                if file.startswith("LinkedIn_Draft_") and file.endswith(".md"):
                    drafts.append(os.path.join(PENDING_POSTS_DIR, file))

            logger.info(f"Found {len(drafts)} pending post drafts")
            return sorted(drafts)

        except Exception as e:
            logger.error(f"Error listing drafts: {str(e)}")
            return []

    def get_post_stats(self) -> Dict[str, Any]:
        """
        Get basic statistics about posting
        Posting ke basic statistics lena

        Returns:
            dict: Statistics dictionary
        """
        # Roman Urdu: Statistics collect karna
        drafts = self.list_pending_posts()

        # Roman Urdu: Profile info lena
        profile_info = None
        if self.is_configured():
            profile_info = self.get_profile_info()

        stats = {
            'pending_drafts': len(drafts),
            'configured': self.is_configured(),
            'test_mode': self.test_mode,
            'client_id': self.client_id[:8] + '...' if self.client_id else 'Not configured',
            'profile': profile_info,
            'vault_path': PENDING_POSTS_DIR
        }

        logger.info(f"Stats: {stats}")
        return stats


def quick_post(text: str = None, test_mode: bool = True):
    """
    Quick post function for easy usage
    Easy usage ke liye quick post function

    Args:
        text: Custom text (optional)
        test_mode: Save as draft if True

    Returns:
        dict: Post result
    """
    # Roman Urdu: Quick poster create karna
    poster = LinkedInPoster(test_mode=test_mode)
    return poster.post_to_linkedin(content=text,
                                   read_from_dashboard=(text is None))


def main():
    """
    Main function with interactive mode
    Interactive mode ke saath main function
    """
    print("=" * 60)
    print("LinkedIn Poster - AI Employee System")
    print("=" * 60)
    print()

    # Roman Urdu: Test mode prompt
    print("Choose mode:")
    print("1. Test Mode (Save drafts only)")
    print("2. Live Mode (Post to LinkedIn)")
    print()

    choice = input("Enter choice (1 or 2, default=1): ").strip()
    test_mode = choice != "2"

    # Roman Urdu: LinkedIn poster initialize karna
    poster = LinkedInPoster(test_mode=test_mode)

    # Roman Urdu: Configuration status dikhana
    print()
    print("Configuration Status:")
    stats = poster.get_post_stats()
    print(f"  - Test Mode: {stats['test_mode']}")
    print(f"  - Configured: {stats['configured']}")
    print(f"  - Client ID: {stats['client_id']}")
    print(f"  - Pending Drafts: {stats['pending_drafts']}")

    if stats['profile']:
        print(f"  - Profile ID: {stats['profile'].get('id', 'N/A')}")

    print()

    # Roman Urdu: Content source prompt
    print("Content Source:")
    print("1. Dashboard.md")
    print("2. Custom Text")
    print()

    content_choice = input("Enter choice (1 or 2, default=1): ").strip()

    if content_choice == "2":
        print()
        custom_text = input("Enter post content: ").strip()
        custom_message = input("Enter custom message (optional): ").strip()
    else:
        custom_text = None
        custom_message = None

    print()
    print("-" * 60)

    # Roman Urdu: Post operation execute karna
    result = poster.post_to_linkedin(
        content=custom_text,
        custom_message=custom_message,
        read_from_dashboard=(content_choice != "2")
    )

    # Roman Urdu: Result display karna
    print()
    print("=" * 60)
    print("Post Result:")
    print("=" * 60)
    print(f"  Status: {'[OK] Success' if result['success'] else '[FAIL] Failed'}")
    print(f"  Mode: {result['mode']}")
    print(f"  Message: {result['message']}")

    if 'post_id' in result:
        print(f"  Post ID: {result['post_id']}")
        print(f"  URL: {result.get('post_url', 'N/A')}")

    if 'draft_path' in result:
        print(f"  Draft Path: {result['draft_path']}")

    print()
    print("Content Preview:")
    print("-" * 60)
    print(result.get('content_preview', 'N/A'))
    print("-" * 60)

    # Roman Urdu: Pending posts list
    drafts = poster.list_pending_posts()
    if drafts:
        print()
        print(f"Pending Drafts ({len(drafts)}):")
        for draft in drafts[-5:]:  # Show last 5
            print(f"  - {os.path.basename(draft)}")

    print()
    print("Check linkedin_poster.log for detailed logs")
    print("=" * 60)


if __name__ == "__main__":
    main()
