import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import markdown

# Load environment variables
load_dotenv()

def read_dashboard_content():
    """
    Read content from Dashboard.md
    Dashboard.md se content padhta hai
    """
    dashboard_path = "../AI_Employee_Vault/Dashboard.md"
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Dashboard.md not found at {dashboard_path}")
        return None
    except Exception as e:
        print(f"Error reading Dashboard.md: {str(e)}")
        return None


def format_business_post(content):
    """
    Format the content into a business post
    Content ko business post mein format karta hai
    """
    # Extract key information from the dashboard content
    lines = content.split('\n')
    title = "Business Update"
    summary = ""
    
    # Look for key sections in the content
    for line in lines:
        if line.startswith('# '):
            title = line.replace('# ', '').strip()
        elif line.startswith('- ') or line.startswith('* '):
            if summary:
                summary += " " + line.replace('- ', '').replace('* ', '').strip()
            else:
                summary = line.replace('- ', '').replace('* ', '').strip()
    
    # Create a formatted business post
    formatted_post = f"{title}\n\n"
    formatted_post += f"{summary}\n\n"
    formatted_post += "For more details, check our latest updates.\n\n"
    formatted_post += "#BusinessUpdate #Automation #AI"
    
    return formatted_post


def post_to_linkedin(post_content):
    """
    Post to LinkedIn using API
    LinkedIn pe API ka istemal karke post karta hai
    """
    linkedin_token = os.getenv("LINKEDIN_TOKEN")
    
    if not linkedin_token:
        print("LinkedIn token not available, saving to pending posts")
        save_pending_post("LinkedIn", post_content)
        return {"success": False, "message": "Token not available"}
    
    try:
        # LinkedIn API endpoint for creating posts
        url = "https://api.linkedin.com/v2/ugcPosts"
        
        headers = {
            "Authorization": f"Bearer {linkedin_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Create the post payload
        payload = {
            "author": f"urn:li:person:{os.getenv('LINKEDIN_PERSON_URN', '')}",  # Need to set this in .env
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            print("Successfully posted to LinkedIn")
            return {"success": True, "message": "Posted to LinkedIn successfully"}
        else:
            print(f"Failed to post to LinkedIn: {response.status_code} - {response.text}")
            return {"success": False, "message": f"Failed to post: {response.status_code}"}
    
    except Exception as e:
        print(f"Error posting to LinkedIn: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}


def post_to_facebook(post_content):
    """
    Post to Facebook using API
    Facebook pe API ka istemal karke post karta hai
    """
    facebook_token = os.getenv("FACEBOOK_TOKEN")
    
    if not facebook_token:
        print("Facebook token not available, saving to pending posts")
        save_pending_post("Facebook", post_content)
        return {"success": False, "message": "Token not available"}
    
    try:
        # Facebook API endpoint for creating posts
        page_id = os.getenv("FACEBOOK_PAGE_ID", "")  # Need to set this in .env
        url = f"https://graph.facebook.com/{page_id}/feed"
        
        params = {
            "message": post_content,
            "access_token": facebook_token
        }
        
        response = requests.post(url, params=params)
        
        if response.status_code == 200:
            print("Successfully posted to Facebook")
            return {"success": True, "message": "Posted to Facebook successfully"}
        else:
            print(f"Failed to post to Facebook: {response.status_code} - {response.text}")
            return {"success": False, "message": f"Failed to post: {response.status_code}"}
    
    except Exception as e:
        print(f"Error posting to Facebook: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}


def save_pending_post(platform, content):
    """
    Save post to Pending_Posts folder if tokens are not available
    Agar tokens available na ho to Pending_Posts folder mein post save karta hai
    """
    pending_posts_dir = "../AI_Employee_Vault/Pending_Posts"
    os.makedirs(pending_posts_dir, exist_ok=True)
    
    # Create a unique filename based on timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pending_{platform.lower()}_{timestamp}.md"
    filepath = os.path.join(pending_posts_dir, filename)
    
    # Create markdown content
    markdown_content = f"""# Pending Social Media Post

**Platform:** {platform}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Post Content:
{content}

---
*This post is awaiting API token for automatic posting.*
"""
    
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(markdown_content)
        print(f"Pending post saved to: {filepath}")
    except Exception as e:
        print(f"Error saving pending post: {str(e)}")


def main():
    """
    Main function to run the social poster
    Social poster chalaney ke liye main function
    """
    print("Reading content from Dashboard.md...")
    dashboard_content = read_dashboard_content()
    
    if not dashboard_content:
        print("No content found in Dashboard.md")
        return
    
    print("Formatting business post...")
    formatted_post = format_business_post(dashboard_content)
    
    print("Posting to LinkedIn...")
    linkedin_result = post_to_linkedin(formatted_post)
    
    print("Posting to Facebook...")
    facebook_result = post_to_facebook(formatted_post)
    
    print("Social posting completed.")
    print(f"LinkedIn: {linkedin_result['message']}")
    print(f"Facebook: {facebook_result['message']}")


if __name__ == "__main__":
    main()