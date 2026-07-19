import os
import requests
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = "onboarding@resend.dev"


def send_otp_email(to_email: str, otp_code: str) -> bool:
    if not RESEND_API_KEY:
        print("WARNING: RESEND_API_KEY not set in environment")
        return False

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": FROM_EMAIL,
                "to": [to_email],
                "subject": "Your NexusAPI Verification Code",
                "text": f"Your verification code is: {otp_code}\n\nThis code will expire in 10 minutes."
            },
            timeout=10
        )
        if response.status_code == 200:
            return True
        else:
            print(f"WARNING: Resend API returned {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"WARNING: Failed to send email due to exception: {e}")
        return False
