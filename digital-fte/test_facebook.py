#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Facebook Token & Connection
Facebook token validate karna aur page info display karna

═══════════════════════════════════════════════════════════════════════════════
USAGE
═══════════════════════════════════════════════════════════════════════════════

python test_facebook.py

This script will:
1. Check if Facebook credentials are configured in .env
2. Validate the access token
3. Display page information
4. Test posting permissions
5. Show token expiry details

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Roman Urdu: Environment variables load karna
load_dotenv()

# Roman Urdu: Configuration
FACEBOOK_API_VERSION = "v18.0"
FACEBOOK_GRAPH_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"


class FacebookTokenTester:
    """
    Facebook Token Validator
    Facebook token ko validate karne wala class
    """

    def __init__(self, page_token: str = None, page_id: str = None):
        """
        Initialize Facebook Token Tester
        Facebook Token Tester ko initialize karna

        Args:
            page_token: Facebook Page Access Token
            page_id: Facebook Page ID
        """
        # Roman Urdu: Credentials lena
        self.page_token = page_token or os.getenv("FACEBOOK_PAGE_TOKEN", "")
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID", "")

        # Roman Urdu: Test results store karna
        self.test_results = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'token_configured': False,
            'page_id_configured': False,
            'token_valid': False,
            'page_accessible': False,
            'permissions': [],
            'page_info': {},
            'errors': []
        }

    def check_configuration(self) -> bool:
        """
        Check if credentials are configured
        Check karo ke credentials configure hain ya nahi

        Returns:
            bool: True if both token and page_id are present
        """
        # Roman Urdu: Token check karna
        self.test_results['token_configured'] = bool(
            self.page_token and self.page_token.strip()
        )

        # Roman Urdu: Page ID check karna
        self.test_results['page_id_configured'] = bool(
            self.page_id and self.page_id.strip()
        )

        # Roman Urdu: Configuration status
        if not self.test_results['token_configured']:
            self.test_results['errors'].append(
                "FACEBOOK_PAGE_TOKEN not found in .env file"
            )
            print("  [FAIL] Token not configured")

        if not self.test_results['page_id_configured']:
            self.test_results['errors'].append(
                "FACEBOOK_PAGE_ID not found in .env file"
            )
            print("  [FAIL] Page ID not configured")

        return (self.test_results['token_configured'] and
                self.test_results['page_id_configured'])

    def validate_token(self) -> bool:
        """
        Validate Facebook access token
        Facebook access token ko validate karna

        Returns:
            bool: True if token is valid
        """
        # Roman Urdu: Token validation start
        print("\n[Step 1] Validating Access Token...")

        if not self.test_results['token_configured']:
            print("  [FAIL] Token not configured")
            return False

        # Roman Urdu: Debug endpoint use karna
        endpoint = f"{FACEBOOK_GRAPH_URL}/debug_token"
        params = {
            'input_token': self.page_token,
            'access_token': f"{self.page_id}|{self.page_token}"
        }

        try:
            # Roman Urdu: API request bhejna
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Roman Urdu: Response check karna
            if 'data' in data:
                token_data = data['data']

                # Roman Urdu: Token validity check
                is_valid = token_data.get('is_valid', False)
                self.test_results['token_valid'] = is_valid

                if is_valid:
                    print(f"  [OK] Token is VALID")

                    # Roman Urdu: Token details extract karna
                    expires_at = token_data.get('expires_at', 'Unknown')
                    if expires_at:
                        expires_datetime = datetime.fromtimestamp(expires_at)
                        expires_str = expires_datetime.strftime("%Y-%m-%d %H:%M:%S")
                        print(f"  [OK] Expires: {expires_str}")

                        # Roman Urdu: Days remaining calculate karna
                        days_remaining = (expires_datetime - datetime.now()).days
                        if days_remaining > 0:
                            print(f"  [OK] Days remaining: {days_remaining}")
                        else:
                            print(f"  [WARN] Token has EXPIRED!")
                            self.test_results['errors'].append("Token has expired")

                    # Roman Urdu: User ID check
                    user_id = token_data.get('user_id', 'Unknown')
                    print(f"  [OK] User ID: {user_id}")

                    # Roman Urdu: App ID check
                    app_id = token_data.get('app_id', 'Unknown')
                    print(f"  [OK] App ID: {app_id}")

                    # Roman Urdu: Scopes/permissions check
                    scopes = token_data.get('scopes', [])
                    self.test_results['permissions'] = scopes
                    print(f"  [OK] Permissions: {', '.join(scopes)}")

                else:
                    print(f"  [FAIL] Token is INVALID")
                    self.test_results['errors'].append("Token is invalid")

                    # Roman Urdu: Error details
                    error_msg = token_data.get('error', {}).get('message', 'Unknown error')
                    print(f"  [FAIL] Error: {error_msg}")
                    self.test_results['errors'].append(error_msg)

            return self.test_results['token_valid']

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(f"  [FAIL] {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            print(f"  [FAIL] {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    def get_page_info(self) -> bool:
        """
        Get Facebook Page information
        Facebook Page ki information lena

        Returns:
            bool: True if page info retrieved successfully
        """
        # Roman Urdu: Page info start
        print("\n[Step 2] Fetching Page Information...")

        if not self.test_results['page_id_configured']:
            print("  [FAIL] Page ID not configured")
            return False

        # Roman Urdu: Graph API endpoint
        endpoint = f"{FACEBOOK_GRAPH_URL}/{self.page_id}"
        params = {
            'fields': 'id,name,username,category,followers_count,likes,about,website,verification_status',
            'access_token': self.page_token
        }

        try:
            # Roman Urdu: API request bhejna
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            page_data = response.json()

            # Roman Urdu: Page info store karna
            self.test_results['page_info'] = page_data
            self.test_results['page_accessible'] = True

            # Roman Urdu: Page details display karna
            print(f"  [OK] Page ID: {page_data.get('id', 'N/A')}")
            print(f"  [OK] Page Name: {page_data.get('name', 'N/A')}")

            if page_data.get('username'):
                print(f"  [OK] Username: @{page_data.get('username')}")

            if page_data.get('category'):
                print(f"  [OK] Category: {page_data.get('category')}")

            if page_data.get('followers_count'):
                print(f"  [OK] Followers: {page_data.get('followers_count'):,}")

            if page_data.get('likes'):
                print(f"  [OK] Likes: {page_data.get('likes'):,}")

            if page_data.get('about'):
                about = page_data.get('about', '')[:100]
                print(f"  [OK] About: {about}...")

            if page_data.get('website'):
                print(f"  [OK] Website: {page_data.get('website')}")

            if page_data.get('verification_status'):
                status = "[OK] Verified" if page_data.get('verification_status') else "[FAIL] Not Verified"
                print(f"  [OK] Verification: {status}")

            return True

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error: {e.response.status_code}"
            print(f"  [FAIL] {error_msg}")

            if e.response.status_code == 400:
                print(f"  [FAIL] Invalid Page ID or Token")
                self.test_results['errors'].append("Invalid Page ID or Token")
            elif e.response.status_code == 403:
                print(f"  [FAIL] Permission denied. Check token permissions.")
                self.test_results['errors'].append("Permission denied")

            self.test_results['errors'].append(error_msg)
            return False

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(f"  [FAIL] {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    def test_posting_permission(self) -> bool:
        """
        Test if we can create posts
        Test karo ke posts create kar sakte hain ya nahi

        Returns:
            bool: True if posting permission exists
        """
        # Roman Urdu: Posting permission test
        print("\n[Step 3] Testing Posting Permissions...")

        required_permissions = [
            'pages_manage_posts',
            'pages_read_engagement',
            'pages_show_list'
        ]

        # Roman Urdu: Permissions check karna
        missing_permissions = []
        for perm in required_permissions:
            if perm not in self.test_results['permissions']:
                missing_permissions.append(perm)

        if missing_permissions:
            print(f"  [FAIL] Missing permissions: {', '.join(missing_permissions)}")
            print(f"  [WARN] You may not be able to post!")
            self.test_results['errors'].append(
                f"Missing permissions: {', '.join(missing_permissions)}"
            )
            return False
        else:
            print(f"  [OK] All required permissions present")
            return True

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all validation tests
        Saare validation tests run karna

        Returns:
            dict: Test results
        """
        # Roman Urdu: Test summary header
        print("=" * 60)
        print("Facebook Token & Connection Test")
        print("=" * 60)
        print(f"Timestamp: {self.test_results['timestamp']}")

        # Roman Urdu: Step 1: Configuration check
        print("\n[Step 0] Checking Configuration...")
        if not self.check_configuration():
            print("  [FAIL] Credentials not configured")
            print("\n  Setup Instructions:")
            print("  1. Open .env file in digital-fte/ folder")
            print("  2. Add FACEBOOK_PAGE_TOKEN and FACEBOOK_PAGE_ID")
            print("  3. See facebook_poster.py for detailed instructions")
            return self.test_results
        else:
            print("  [OK] Credentials configured")

        # Roman Urdu: Step 2: Token validation
        self.validate_token()

        # Roman Urdu: Step 3: Page info
        if self.test_results['token_valid']:
            self.get_page_info()

        # Roman Urdu: Step 4: Posting permission
        if self.test_results['page_accessible']:
            self.test_posting_permission()

        # Roman Urdu: Final summary
        self.print_summary()

        return self.test_results

    def print_summary(self):
        """
        Print test summary
        Test summary print karna
        """
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)

        # Roman Urdu: Success count
        checks = [
            ("Token Configured", self.test_results['token_configured']),
            ("Page ID Configured", self.test_results['page_id_configured']),
            ("Token Valid", self.test_results['token_valid']),
            ("Page Accessible", self.test_results['page_accessible']),
            ("Posting Permissions", 
             all(p in self.test_results['permissions'] 
                 for p in ['pages_manage_posts', 'pages_read_engagement', 'pages_show_list']))
        ]

        # Roman Urdu: Check results display
        for check_name, passed in checks:
            status = "[OK] PASS" if passed else "[FAIL] FAIL"
            print(f"  {status}: {check_name}")

        # Roman Urdu: Errors display
        if self.test_results['errors']:
            print("\n  Errors:")
            for error in self.test_results['errors']:
                print(f"    • {error}")

        # Roman Urdu: Overall status
        print("\n" + "-" * 60)
        if all(check[1] for check in checks[:4]):
            print("  [SUCCESS] ALL TESTS PASSED! Ready to post!")
            print("  Run: python facebook_poster.py")
        else:
            print("  [WARN] Some tests failed. Please fix the issues above.")
            print("  See facebook_poster.py for setup instructions.")
        print("-" * 60)

    def save_test_results(self, filename: str = "facebook_test_results.json"):
        """
        Save test results to JSON file
        Test results ko JSON file mein save karna

        Args:
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, default=str)

            print(f"\n  [OK] Test results saved to: {filename}")
        except Exception as e:
            print(f"\n  [FAIL] Could not save results: {str(e)}")


def main():
    """
    Main function
    Roman Urdu: Main function
    """
    # Roman Urdu: Token tester create karna
    tester = FacebookTokenTester()

    # Roman Urdu: Tests run karna
    results = tester.run_all_tests()

    # Roman Urdu: Save results (optional)
    try:
        save_choice = input("\nSave test results to JSON file? (y/n, default=n): ").strip().lower()
        if save_choice == 'y':
            tester.save_test_results()
    except EOFError:
        # Non-interactive mode - skip saving
        pass

    # Roman Urdu: Exit code
    if results['token_valid'] and results['page_accessible']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()
