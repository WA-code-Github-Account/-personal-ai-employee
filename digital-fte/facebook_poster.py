#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Poster - Social Media Automation for AI Employee
Facebook Page par posts automate karne wala module
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
VAULT_BASE = "D:/AI_Workspace_bronze_silver_gold/AI_Employee_Vault"
PENDING_POSTS_DIR = os.path.join(VAULT_BASE, "Pending_Posts")
DASHBOARD_PATH = os.path.join(VAULT_BASE, "Dashboard.md")

# Roman Urdu: Facebook API configuration
FACEBOOK_API_VERSION = "v18.0"
FACEBOOK_GRAPH_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"

# Roman Urdu: Logging setup
LOG_FILE = "facebook_poster.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FacebookPoster:
    """
    Facebook Page Poster for AI Employee System
    AI Employee System ke liye Facebook Page poster
    """

    def __init__(self, page_token: str = None, page_id: str = None, test_mode: bool = False):
        """
        Initialize Facebook Poster
        Facebook Poster ko initialize karna
        
        Args:
            page_token: Facebook Page Access Token
            page_id: Facebook Page ID
            test_mode: If True, save drafts without posting
        """
        # Roman Urdu: Configuration se credentials lena
        self.page_token = page_token or os.getenv("FACEBOOK_PAGE_TOKEN", "")
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID", "")
        self.test_mode = test_mode
        
        # Roman Urdu: Pending posts directory ensure karna
        os.makedirs(PENDING_POSTS_DIR, exist_ok=True)
        
        # Roman Urdu: Initialization log
        if self.test_mode:
            logger.info("Facebook Poster initialized in TEST MODE")
            logger.info("Posts will be saved as drafts, not published")
        else:
            logger.info(f"Facebook Poster initialized for Page ID: {self.page_id}")
        
        # Roman Urdu: Audit log
        log_task_start("Facebook Poster Init", source="facebook_poster", 
                      test_mode=str(test_mode))

    def is_configured(self) -> bool:
        """
        Check if Facebook credentials are configured
        Check karo ke Facebook credentials configure hain ya nahi
        
        Returns:
            bool: True if both token and page_id are available
        """
        # Roman Urdu: Credentials check karna
        has_token = bool(self.page_token and self.page_token.strip())
        has_id = bool(self.page_id and self.page_id.strip())
        
        if not has_token:
            logger.warning("FACEBOOK_PAGE_TOKEN not configured")
        if not has_id:
            logger.warning("FACEBOOK_PAGE_ID not configured")
        
        return has_token and has_id

    def read_dashboard_content(self) -> Optional[str]:
        """
        Read content from Dashboard.md
        Dashboard.md se content parhna
        
        Returns:
            str: Dashboard content or None if error
        """
        # Roman Urdu: Audit log for file read
        log_file_operation("READ", DASHBOARD_PATH, source="facebook_poster")
        
        try:
            if not os.path.exists(DASHBOARD_PATH):
                logger.warning(f"Dashboard.md not found: {DASHBOARD_PATH}")
                return None
            
            with open(DASHBOARD_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Roman Urdu: Audit log for successful read
            log_file_operation("READ", DASHBOARD_PATH, result="SUCCESS", 
                              file_size=len(content), source="facebook_poster")
            
            logger.info(f"Read Dashboard.md ({len(content)} characters)")
            return content
            
        except Exception as e:
            logger.error(f"Error reading Dashboard.md: {str(e)}")
            log_error("DASHBOARD_READ_ERROR", str(e), 
                     file_involved=DASHBOARD_PATH, action="read_dashboard_content")
            return None

    def format_post_content(self, content: str, custom_message: str = None) -> str:
        """
        Format content for Facebook post
        Content ko Facebook post ke liye format karna
        
        Args:
            content: Raw content to format
            custom_message: Optional custom message to prepend
        
        Returns:
            str: Formatted Facebook post content
        """
        # Roman Urdu: Post formatting shuru karna
        logger.info("Formatting content for Facebook post")
        
        # Roman Urdu: Timestamp add karna
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Roman Urdu: Custom message ya default header
        if custom_message:
            header = custom_message
        else:
            header = f"🤖 AI Employee System Update"
        
        # Roman Urdu: Content ko clean karna (remove markdown headers)
        clean_content = content
        for i in range(6, 0, -1):
            clean_content = clean_content.replace('#' * i + ' ', '')
        
        # Roman Urdu: Lines ko limit karna (Facebook has character limits)
        lines = clean_content.split('\n')
        max_lines = 15
        if len(lines) > max_lines:
            clean_content = '\n'.join(lines[:max_lines]) + '\n\n... (truncated)'
        
        # Roman Urdu: Final formatted post
        formatted_post = f"""{header}

{clean_content}

---
📅 Posted: {timestamp}
🔧 AI Employee System - Gold Tier
#AIEmployee #Automation #Productivity"""
        
        logger.info(f"Formatted post ({len(formatted_post)} characters)")
        return formatted_post

    def create_post_draft(self, content: str, image_path: str = None, 
                         message: str = None) -> str:
        """
        Create a post draft file
        Post draft file banana
        
        Args:
            content: Post content
            image_path: Optional image path
            message: Optional custom message
        
        Returns:
            str: Path to draft file
        """
        # Roman Urdu: Draft file ka naam aur path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_filename = f"Facebook_Draft_{timestamp}.md"
        draft_path = os.path.join(PENDING_POSTS_DIR, draft_filename)
        
        # Roman Urdu: Draft content create karna
        draft_content = f"""# Facebook Post Draft

## Status: Pending Review

## Post Details
- **Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Platform:** Facebook Page
- **Test Mode:** {self.test_mode}

## Content
{content}

## Image
{"```" + image_path + "```" if image_path else "*No image attached*"}

## Custom Message
{message if message else "*Using default message*"}

## Action Required
Review this draft and either:
1. Change status to "Approved" to enable posting
2. Change status to "Rejected" to discard
3. Edit content and save

---
*Generated by AI Employee Facebook Poster*
"""
        
        # Roman Urdu: Draft file save karna
        try:
            with open(draft_path, 'w', encoding='utf-8') as f:
                f.write(draft_content)
            
            # Roman Urdu: Audit log
            log_file_operation("WRITE", draft_path, result="SUCCESS", 
                              file_size=len(draft_content), source="facebook_poster")
            
            logger.info(f"Draft saved: {draft_path}")
            return draft_path
            
        except Exception as e:
            logger.error(f"Error saving draft: {str(e)}")
            log_error("DRAFT_SAVE_ERROR", str(e), 
                     file_involved=draft_path, action="create_post_draft")
            raise

    @retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
    def post_to_facebook_api(self, content: str, image_path: str = None) -> Dict[str, Any]:
        """
        Post to Facebook Page using Graph API
        Facebook Graph API se Page par post karna
        
        Args:
            content: Formatted post content
            image_path: Optional path to image file
        
        Returns:
            dict: Facebook API response
        """
        # Roman Urdu: API request prepare karna
        endpoint = f"{FACEBOOK_GRAPH_URL}/{self.page_id}/feed"
        
        # Roman Urdu: Request parameters
        params = {
            'message': content,
            'access_token': self.page_token
        }
        
        # Roman Urdu: Image attachment handle karna
        files = {}
        if image_path and os.path.exists(image_path):
            try:
                files['source'] = open(image_path, 'rb')
                logger.info(f"Attaching image: {image_path}")
            except Exception as e:
                logger.warning(f"Could not attach image: {str(e)}")
        
        # Roman Urdu: API call log
        logger.info(f"Posting to Facebook Page: {self.page_id}")
        log_task_start("Facebook API Post", file_involved=image_path or "text-only",
                      source="facebook_poster")
        
        try:
            # Roman Urdu: POST request bhejna
            response = requests.post(endpoint, data=params, files=files, timeout=30)
            
            # Roman Urdu: Response check karna
            response.raise_for_status()
            result = response.json()
            
            # Roman Urdu: Success log
            logger.info(f"Facebook post successful: {result}")
            log_task_complete("Facebook API Post", result="SUCCESS", 
                             source="facebook_poster")
            
            return {
                'success': True,
                'post_id': result.get('id'),
                'response': result
            }
            
        except requests.exceptions.HTTPError as e:
            # Roman Urdu: HTTP error handle karna
            error_msg = f"Facebook API HTTP Error: {str(e)}"
            logger.error(error_msg)
            log_error("FACEBOOK_HTTP_ERROR", str(e), action="post_to_facebook_api")
            return {
                'success': False,
                'error': error_msg,
                'status_code': e.response.status_code if hasattr(e, 'response') else None
            }
            
        except requests.exceptions.RequestException as e:
            # Roman Urdu: Network error handle karna
            error_msg = f"Network error: {str(e)}"
            logger.error(error_msg)
            log_error("FACEBOOK_NETWORK_ERROR", str(e), action="post_to_facebook_api")
            return {
                'success': False,
                'error': error_msg
            }
            
        finally:
            # Roman Urdu: File handle close karna
            if files and 'source' in files:
                files['source'].close()

    def post_to_facebook(self, content: str = None, image_path: str = None,
                        custom_message: str = None, 
                        read_from_dashboard: bool = True) -> Dict[str, Any]:
        """
        Main function to post to Facebook
        Facebook par post karne ka main function
        
        Args:
            content: Custom content (overrides dashboard if provided)
            image_path: Optional path to image file
            custom_message: Optional custom message
            read_from_dashboard: If True, read content from Dashboard.md
        
        Returns:
            dict: Result with success status and post/draft info
        """
        # Roman Urdu: Post operation start karna
        logger.info("=" * 60)
        logger.info("Facebook Post Operation Started")
        logger.info("=" * 60)
        
        log_task_start("Facebook Post", source="facebook_poster",
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
        formatted_content = self.format_post_content(content, custom_message)
        
        # Roman Urdu: Step 3: Test mode check
        if self.test_mode or not self.is_configured():
            logger.info("Test mode or not configured - saving as draft")
            
            # Roman Urdu: Draft save karna
            draft_path = self.create_post_draft(formatted_content, image_path, custom_message)
            
            result = {
                'success': True,
                'mode': 'draft',
                'draft_path': draft_path,
                'message': 'Post saved as draft (test mode or not configured)',
                'content_preview': formatted_content[:200] + '...' if len(formatted_content) > 200 else formatted_content
            }
            
            logger.info(f"Draft created: {draft_path}")
            log_task_complete("Facebook Post", result="DRAFT_SAVED", 
                             source="facebook_poster")
            
            return result
        
        # Roman Urdu: Step 4: Actual Facebook post
        logger.info("Posting to Facebook...")
        api_result = self.post_to_facebook_api(formatted_content, image_path)
        
        if api_result['success']:
            # Roman Urdu: Post confirmation
            result = {
                'success': True,
                'mode': 'published',
                'post_id': api_result['post_id'],
                'post_url': f"https://facebook.com/{api_result['post_id']}",
                'message': 'Post published successfully',
                'content_preview': formatted_content[:200] + '...' if len(formatted_content) > 200 else formatted_content
            }
            
            logger.info(f"Post published: {api_result['post_id']}")
            log_task_complete("Facebook Post", result="PUBLISHED", 
                             source="facebook_poster")
        else:
            # Roman Urdu: Post failed - save as draft
            logger.warning("Post failed - saving as draft")
            draft_path = self.create_post_draft(formatted_content, image_path, custom_message)
            
            result = {
                'success': False,
                'mode': 'failed_to_draft',
                'draft_path': draft_path,
                'error': api_result.get('error', 'Unknown error'),
                'message': 'Post failed, saved as draft',
                'content_preview': formatted_content[:200] + '...' if len(formatted_content) > 200 else formatted_content
            }
            
            log_task_complete("Facebook Post", result="FAILED", 
                             error=api_result.get('error', 'Unknown'),
                             source="facebook_poster")
        
        logger.info("=" * 60)
        logger.info("Facebook Post Operation Complete")
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
                if file.startswith("Facebook_Draft_") and file.endswith(".md"):
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
        
        stats = {
            'pending_drafts': len(drafts),
            'configured': self.is_configured(),
            'test_mode': self.test_mode,
            'page_id': self.page_id[:10] + '...' if self.page_id else 'Not configured',
            'vault_path': PENDING_POSTS_DIR
        }
        
        logger.info(f"Stats: {stats}")
        return stats


def quick_post(text: str = None, image: str = None, test_mode: bool = True):
    """
    Quick post function for easy usage
    Easy usage ke liye quick post function
    
    Args:
        text: Custom text (optional)
        image: Image path (optional)
        test_mode: Save as draft if True
    
    Returns:
        dict: Post result
    """
    # Roman Urdu: Quick poster create karna
    poster = FacebookPoster(test_mode=test_mode)
    return poster.post_to_facebook(content=text, image_path=image, 
                                   read_from_dashboard=(text is None))


def main():
    """
    Main function with interactive mode
    Interactive mode ke saath main function
    """
    print("=" * 60)
    print("Facebook Poster - AI Employee System")
    print("=" * 60)
    print()
    
    # Roman Urdu: Test mode prompt
    print("Choose mode:")
    print("1. Test Mode (Save drafts only)")
    print("2. Live Mode (Post to Facebook)")
    print()
    
    choice = input("Enter choice (1 or 2, default=1): ").strip()
    test_mode = choice != "2"
    
    # Roman Urdu: Facebook poster initialize karna
    poster = FacebookPoster(test_mode=test_mode)
    
    # Roman Urdu: Configuration status dikhana
    print()
    print("Configuration Status:")
    stats = poster.get_post_stats()
    print(f"  - Test Mode: {stats['test_mode']}")
    print(f"  - Configured: {stats['configured']}")
    print(f"  - Page ID: {stats['page_id']}")
    print(f"  - Pending Drafts: {stats['pending_drafts']}")
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
        image_path = input("Enter image path (optional): ").strip()
        
        if not image_path:
            image_path = None
    else:
        custom_text = None
        custom_message = None
        image_path = input("Enter image path (optional): ").strip()
        if not image_path:
            image_path = None
    
    print()
    print("-" * 60)
    
    # Roman Urdu: Post operation execute karna
    result = poster.post_to_facebook(
        content=custom_text,
        image_path=image_path,
        custom_message=custom_message,
        read_from_dashboard=(content_choice != "2")
    )
    
    # Roman Urdu: Result display karna
    print()
    print("=" * 60)
    print("Post Result:")
    print("=" * 60)
    print(f"  Status: {'✓ Success' if result['success'] else '✗ Failed'}")
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
    print("Check facebook_poster.log for detailed logs")
    print("=" * 60)


if __name__ == "__main__":
    main()
