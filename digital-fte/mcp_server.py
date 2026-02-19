import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading

# Load environment variables
load_dotenv()

# Global variable to store pending approvals
pending_approvals = {}

def send_email_tool(recipient, subject, body):
    """
    Send email tool that handles email sending with approval workflow
    Email bhejne ka tool jo approval workflow ko handle karta hai
    """
    # Generate unique ID for this email
    email_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(recipient + subject) % 10000}"
    
    # Create approval file path
    approval_dir = "../AI_Employee_Vault/Pending_Approval"
    os.makedirs(approval_dir, exist_ok=True)
    
    approval_file = os.path.join(approval_dir, f"{email_id}.md")
    
    # Create approval markdown content
    approval_content = f"""# Email Approval Required

**ID:** {email_id}

## Email Details
- **Recipient:** {recipient}
- **Subject:** {subject}
- **Body:**
{body}

## Approval Status
- **Status:** Pending
- **Requested:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Action Required
Type "YES" to approve this email, or "NO" to reject it.
"""
    
    # Write approval file
    with open(approval_file, 'w', encoding='utf-8') as f:
        f.write(approval_content)
    
    print(f"Approval file created: {approval_file}")
    print(f"Recipient: {recipient}")
    print(f"Subject: {subject}")
    print("Waiting for approval...")
    
    # Ask user for approval in terminal
    while True:
        user_input = input("Type 'YES' to approve and send email, 'NO' to reject: ").strip().upper()
        if user_input == "YES":
            result = actually_send_email(recipient, subject, body)
            # Update approval file
            with open(approval_file, 'a') as f:
                f.write(f"\n\n**Approved:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Result:** {result}")
            return {"result": result}
        elif user_input == "NO":
            # Update approval file
            with open(approval_file, 'a') as f:
                f.write(f"\n\n**Rejected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("**Result:** Email rejected by user")
            return {"result": "Email rejected by user"}
        else:
            print("Invalid input. Please type 'YES' to approve or 'NO' to reject.")


def actually_send_email(recipient, subject, body):
    """
    Actually send the email via Gmail SMTP
    Gmail SMTP ke zariye email asal mein bhejta hai
    """
    try:
        # Get email credentials from environment variables
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("EMAIL_ADDRESS")
        sender_password = os.getenv("EMAIL_PASSWORD")
        
        if not sender_email or not sender_password:
            raise ValueError("Email credentials not found in .env file")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient, text)
        server.quit()
        
        print(f"Email sent successfully to {recipient}")
        return f"Email sent successfully to {recipient}"
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return f"Error sending email: {str(e)}"


# Create Flask app
app = Flask(__name__)

@app.route('/call', methods=['POST'])
def handle_call():
    """
    Handle incoming MCP calls
    Ane wale MCP calls ko handle karta hai
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'method' not in data:
            return jsonify({"error": {"code": -32600, "message": "Missing method"}}), 400
            
        method = data['method']
        
        # Handle send_email method
        if method == 'send_email':
            if 'params' not in data:
                return jsonify({"error": {"code": -32602, "message": "Missing params"}}), 400
                
            params = data['params']
            
            # Validate required parameters
            required_params = ['recipient', 'subject', 'body']
            for param in required_params:
                if param not in params:
                    return jsonify({"error": {"code": -32602, "message": f"Missing parameter: {param}"}}), 400
            
            # Call the send_email function
            result = send_email_tool(params['recipient'], params['subject'], params['body'])
            
            return jsonify({
                "jsonrpc": "2.0",
                "result": result,
                "id": data.get('id')
            })
        else:
            return jsonify({"error": {"code": -32601, "message": f"Method not found: {method}"}}), 404
            
    except Exception as e:
        print(f"Error handling call: {str(e)}")
        return jsonify({"error": {"code": -32603, "message": "Internal error"}}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Health check ka endpoint
    """
    return jsonify({"status": "ok"})


def main():
    """
    Main function to start the MCP server
    MCP server shuru karne ke liye main function
    """
    # Create pending approval directory if it doesn't exist
    approval_dir = "../AI_Employee_Vault/Pending_Approval"
    os.makedirs(approval_dir, exist_ok=True)
    
    print("Starting MCP Server...")
    app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()