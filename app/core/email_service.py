import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def send_otp_email(to_email: str, otp_code: str) -> bool:
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("WARNING: Email service credentials missing in .env")
        return False
        
    msg = EmailMessage()
    msg["Subject"] = "Your NexusAPI Verification Code"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_email
    
    body = f"Your verification code is: {otp_code}\n\nThis code will expire in 10 minutes."
    msg.set_content(body)
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"WARNING: Failed to send email due to exception: {str(e)}")
        return False
