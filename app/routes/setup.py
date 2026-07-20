"""
One-time setup endpoint to promote a user to admin.
Protected by a secret key from environment variables.
DELETE THIS FILE after initial admin setup is complete.
"""

import os
from fastapi import APIRouter, HTTPException
from sqlite3 import Connection
from fastapi import Depends
from app.db.database import get_db

router = APIRouter()

SETUP_SECRET = os.getenv("SETUP_SECRET", "")


@router.post("/promote-to-admin")
def promote_to_admin(email: str, secret: str, db: Connection = Depends(get_db)):
    if not SETUP_SECRET or secret != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute("UPDATE users SET role = 'admin' WHERE email = ?", (email,))
    db.commit()

    return {"message": f"{email} is now an admin"}
