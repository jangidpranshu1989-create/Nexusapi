import random
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlite3 import Connection
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.developer import RequestOTP, VerifyOTP
from app.core.email_service import send_otp_email

router = APIRouter()

@router.post("/request-verification")
def request_verification(db: Connection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    otp_code = f"{random.randint(100000, 999999)}"
    
    # SQLite structure handles naive strings or ISO formats; use current UTC plus 10 minutes
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO otp_codes (user_id, code, purpose, expires_at, is_used) VALUES (?, ?, ?, ?, 0)",
        (current_user["id"], otp_code, "developer_verification", expires_at)
    )
    db.commit()
    
    send_otp_email(current_user["email"], otp_code)
    
    return {"message": "OTP sent to your email"}

@router.post("/verify")
def verify_developer(payload: VerifyOTP, db: Connection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    now = datetime.now(timezone.utc).isoformat()
    cursor = db.cursor()
    
    cursor.execute(
        """SELECT id FROM otp_codes 
           WHERE user_id = ? AND code = ? AND purpose = 'developer_verification' 
           AND is_used = 0 AND expires_at > ? 
           ORDER BY created_at DESC LIMIT 1""",
        (current_user["id"], payload.code, now)
    )
    otp_row = cursor.fetchone()
    
    if not otp_row:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
        
    cursor.execute("UPDATE otp_codes SET is_used = 1 WHERE id = ?", (otp_row["id"],))
    
    cursor.execute(
        "UPDATE users SET role = 'developer', is_email_verified = 1 WHERE id = ?",
        (current_user["id"],)
    )
    db.commit()
    
    return {"message": "You are now a verified developer", "role": "developer"}
