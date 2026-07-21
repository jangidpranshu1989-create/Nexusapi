"""
User settings routes: profile info, appearance, security, data control.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlite3 import Connection
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import hash_password, verify_password

router = APIRouter()


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class AppearanceUpdate(BaseModel):
    accent_color: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class NotificationSettings(BaseModel):
    email_notifications: bool


@router.get("/full-profile")
def get_full_profile(db: Connection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, email, name, role, avatar_url, bio, accent_color, email_notifications, is_email_verified, created_at FROM users WHERE id = ?",
        (current_user["id"],)
    )
    return dict(cursor.fetchone())


@router.put("/profile")
def update_profile(payload: ProfileUpdate, db: Connection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cursor = db.cursor()
    updates, params = [], []

    if payload.name is not None:
        updates.append("name = ?")
        params.append(payload.name)
    if payload.bio is not None:
        updates.append("bio = ?")
        params.append(payload.bio)
    if payload.avatar_url is not None:
        updates.append("avatar_url = ?")
        params.append(payload.avatar_url)

    if not updates:
        raise HTTPException(400, "No fields to update")

    params.append(current_user["id"])
    cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
    db.commit()
    return {"message": "Profile updated"}


@router.put("/appearance")
def update_appearance(payload: AppearanceUpdate, db: Connection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET accent_color = ? WHERE id = ?", (payload.accent_color, current_user["id"]))
    db.commit()
    return {"message": "Appearance updated", "accent_color": payload.accent_color}


@router.put("/notifications")
def update_notifications(payload: NotificationSettings, db: Connection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET email_notifications = ? WHERE id = ?", (int(payload.email_notifications), current_user["id"]))
    db.commit()
    return {"message": "Notification preferences updated"}


@router.put("/password")
def change_password(payload: PasswordChange, db: Connection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cursor = db.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (current_user["id"],))
    row = cursor.fetchone()

    if not verify_password(payload.current_password, row["password_hash"]):
        raise HTTPException(400, "Current password is incorrect")

    new_hash = hash_password(payload.new_password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, current_user["id"]))
    db.commit()
    return {"message": "Password changed successfully"}


@router.get("/export-data")
def export_my_data(db: Connection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cursor = db.cursor()
    cursor.execute("SELECT id, email, name, role, bio, created_at FROM users WHERE id = ?", (current_user["id"],))
    user = dict(cursor.fetchone())

    cursor.execute("SELECT id, title, slug, downloads, created_at FROM systems WHERE owner_id = ?", (current_user["id"],))
    systems = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT id, system_id, rating, comment, created_at FROM reviews WHERE user_id = ?", (current_user["id"],))
    reviews = [dict(r) for r in cursor.fetchall()]

    return {"user": user, "systems": systems, "reviews": reviews}


@router.delete("/account")
def delete_account(db: Connection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cursor = db.cursor()
    cursor.execute("UPDATE systems SET is_active = 0 WHERE owner_id = ?", (current_user["id"],))
    cursor.execute("DELETE FROM users WHERE id = ?", (current_user["id"],))
    db.commit()
    return {"message": "Account deleted"}
