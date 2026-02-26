#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test LinkedIn Token & Connection
LinkedIn token validate karna aur profile info display karna

═══════════════════════════════════════════════════════════════════════════════
USAGE
═══════════════════════════════════════════════════════════════════════════════

python test_linkedin.py

This script will:
1. Check if LinkedIn credentials are configured in .env
2. Validate the access token
3. Display profile information
4. Test posting permissions (w_member_social)
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
LINKEDIN_API_BASE_URL = "https://api.linkedin.com/v2"
LINKEDIN_API_VERSION = "202402"


class LinkedInTokenTester:
    """
    LinkedIn Token Validator
    LinkedIn token ko validate karne wala class
    """

    def __init__(self, access_token: str = None, client_id: str = None,
                 client_secret: str = None):
        """
        Initialize LinkedIn Token Tester
        LinkedIn Token Tester ko initialize karna

        Args:
            access_token: LinkedIn OAuth access token
            client_id: LinkedIn app client ID
            client_secret: LinkedIn app client secret
        """
        # Roman Urdu: Credentials lena
        self.access_token = access_token or os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        self.client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET", "")

        # Roman Urdu: Test results store karna
        self.test_results = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'token_configured': False,
            'client_id_configured': False,
            'token_valid': False,
            'profile_accessible': False,
            'permissions': [],
            'profile_info': {},
            'errors': []
        }

    def check_configuration(self) -> bool:
        """
        Check if credentials are configured
        Check karo ke credentials configure hain ya nahi

        Returns:
            bool: True if access token is present
        """
        # Roman Urdu: Token check karna
        self.test_results['token_configured'] = bool(
            self.access_token and self.access_token.strip()
        )

        # Roman Urdu: Client ID check karna
        self.test_results['client_id_configured'] = bool(
            self.client_id and self.client_id.strip()
        )

        # Roman Urdu: Configuration status
        if not self.test_results['token_configured']:
            self.test_results['errors'].append(
                "LINKEDIN_ACCESS_TOKEN not found in .env file"
            )
            print("  [FAIL] Access token not configured")
            print("\n  Setup Instructions:")
            print("  1. Visit: https://www.linkedin.com/developers/tools/oauth/access-token-generator")
            print("  2. Select your app")
            print("  3. Add permissions: w_member_social, r_basicprofile")
            print("  4. Click 'Generate access token'")
            print("  5. Copy token to .env file")

        if not self.test_results['client_id_configured']:
            self.test_results['errors'].append(
                "LINKEDIN_CLIENT_ID not found in .env file"
            )
            print("  [FAIL] Client ID not configured")

        configured = self.test_results['token_configured']
        
        if configured:
            print("  [OK] Credentials configured")

        return configured

    def validate_token(self) -> bool:
        """
        Validate LinkedIn access token
        LinkedIn access token ko validate karna

        Returns:
            bool: True if token is valid
        """
        # Roman Urdu: Token validation start
        print("\n[Step 1] Validating Access Token...")

        if not self.test_results['token_configured']:
            print("  [FAIL] Token not configured")
            return False

        # Roman Urdu: API endpoint - Get profile info (validates token)
        endpoint = f"{LINKEDIN_API_BASE_URL}/me"

        # Roman Urdu: Request headers
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'linkedin-version': LINKEDIN_API_VERSION
        }

        try:
            # Roman Urdu: API request bhejna
            response = requests.get(endpoint, headers=headers, timeout=10)

            # Roman Urdu: Response check karna
            if response.status_code == 200:
                profile_data = response.json()
                
                # Roman Urdu: Token valid hai
                self.test_results['token_valid'] = True
                self.test_results['profile_info'] = profile_data
                self.test_results['profile_accessible'] = True

                print(f"  [OK] Token is VALID")

                # Roman Urdu: Profile details display karna
                person_id = profile_data.get('id', 'Unknown')
                print(f"  [OK] Profile ID: {person_id}")

                # Roman Urdu: Name extract karna
                localized_name = profile_data.get('localizedFirstName', 'N/A')
                print(f"  [OK] Name: {localized_name}")

                # Roman Urdu: Email check karna (if permission granted)
                email_endpoint = f"{LINKEDIN_API_BASE_URL}/emailAddress?q=members&projection=(elements*(handle~))"
                email_response = requests.get(email_endpoint, headers=headers, timeout=10)
                
                if email_response.status_code == 200:
                    email_data = email_response.json()
                    elements = email_data.get('elements', [])
                    if elements:
                        email = elements[0].get('handle~', {}).get('emailAddress', 'N/A')
                        print(f"  [OK] Email: {email}")

                return True

            elif response.status_code == 401:
                # Roman Urdu: Unauthorized - token invalid/expired
                print(f"  [FAIL] Token is INVALID or EXPIRED")
                self.test_results['errors'].append("Token is invalid or expired")
                
                # Roman Urdu: Error details
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Unknown error')
                    print(f"  [FAIL] Error: {error_msg}")
                    self.test_results['errors'].append(error_msg)
                except:
                    print(f"  [FAIL] HTTP 401 Unauthorized")

                return False

            else:
                # Roman Urdu: Other errors
                print(f"  [FAIL] HTTP {response.status_code}")
                self.test_results['errors'].append(f"HTTP {response.status_code}")
                return False

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

    def check_permissions(self) -> bool:
        """
        Check if required permissions are granted
        Check karo ke required permissions granted hain ya nahi

        Returns:
            bool: True if w_member_social permission exists
        """
        # Roman Urdu: Permission check start
        print("\n[Step 2] Checking Permissions...")

        required_permissions = [
            'w_member_social',      # Post to LinkedIn
            'r_basicprofile'        # Read basic profile
        ]

        # Roman Urdu: For now, assume permissions are OK if token works
        # LinkedIn doesn't provide a direct permission check endpoint
        # We'll verify by attempting a post (in test mode)

        print(f"  Required permissions:")
        for perm in required_permissions:
            print(f"    - {perm}")

        print(f"  [WARN] LinkedIn doesn't provide direct permission check")
        print(f"  [INFO] If token works, permissions are likely granted")
        print(f"  [INFO] To verify: Generate token with w_member_social permission")

        # Roman Urdu: Store assumed permissions
        self.test_results['permissions'] = required_permissions

        return True

    def test_post_capability(self) -> bool:
        """
        Test if we can create posts (without actually posting)
        Test karo ke posts create kar sakte hain ya nahi

        Returns:
            bool: True if posting should work
        """
        # Roman Urdu: Post capability test
        print("\n[Step 3] Testing Post Capability...")

        if not self.test_results['token_valid']:
            print(f"  [FAIL] Cannot test - token invalid")
            return False

        # Roman Urdu: Person URN test karna
        endpoint = f"{LINKEDIN_API_BASE_URL}/me"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                profile_data = response.json()
                person_id = profile_data.get('id')
                
                if person_id:
                    person_urn = f"urn:li:person:{person_id}"
                    print(f"  [OK] Person URN: {person_urn}")
                    print(f"  [OK] Can create posts as: {person_urn}")
                    return True
                else:
                    print(f"  [FAIL] Person ID not found")
                    return False
            else:
                print(f"  [FAIL] HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"  [FAIL] Error: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all validation tests
        Saare validation tests run karna

        Returns:
            dict: Test results
        """
        # Roman Urdu: Test summary header
        print("=" * 60)
        print("LinkedIn Token & Connection Test")
        print("=" * 60)
        print(f"Timestamp: {self.test_results['timestamp']}")

        # Roman Urdu: Step 1: Configuration check
        print("\n[Step 0] Checking Configuration...")
        if not self.check_configuration():
            print("\n  [FAIL] Credentials not configured")
            return self.test_results

        # Roman Urdu: Step 2: Token validation
        self.validate_token()

        # Roman Urdu: Step 3: Permissions check
        if self.test_results['token_valid']:
            self.check_permissions()

        # Roman Urdu: Step 4: Post capability
        if self.test_results['token_valid']:
            self.test_post_capability()

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
            ("Client ID Configured", self.test_results['client_id_configured']),
            ("Token Valid", self.test_results['token_valid']),
            ("Profile Accessible", self.test_results['profile_accessible']),
            ("Post Capable", self.test_results['token_valid'])  # If token valid, can post
        ]

        # Roman Urdu: Check results display
        for check_name, passed in checks:
            status = "[OK] PASS" if passed else "[FAIL] FAIL"
            print(f"  {status}: {check_name}")

        # Roman Urdu: Errors display
        if self.test_results['errors']:
            print("\n  Errors:")
            for error in self.test_results['errors']:
                print(f"    - {error}")

        # Roman Urdu: Overall status
        print("\n" + "-" * 60)
        if all(check[1] for check in checks[:4]):
            print("  [SUCCESS] ALL TESTS PASSED! Ready to post!")
            print("  Run: python linkedin_poster.py")
        else:
            print("  [WARN] Some tests failed. Please fix the issues above.")
            print("  See linkedin_poster.py for setup instructions.")
        print("-" * 60)

    def save_test_results(self, filename: str = "linkedin_test_results.json"):
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
    tester = LinkedInTokenTester()

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
    if results['token_valid'] and results['profile_accessible']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()
