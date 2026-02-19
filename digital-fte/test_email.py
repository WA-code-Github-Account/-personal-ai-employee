import requests
import json

def test_send_email():
    """
    Test function to send email via MCP server
    MCP server ke zariye email bhejne ka test function
    """
    url = "http://localhost:3000/call"
    
    # Prepare the JSON payload
    payload = {
        "method": "send_email",
        "params": {
            "recipient": "wahishaikh545@gmail.com",
            "subject": "Test Email",
            "body": "Hello from AI Employee"
        }
    }
    
    # Set the content type header
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Send the POST request
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

if __name__ == "__main__":
    print("Testing send_email via MCP server...")
    test_send_email()