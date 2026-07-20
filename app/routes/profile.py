"""
User profile routes - view own profile info, systems created, reviews given.
"""

from fastapi import APIRouter, Depends
from sqlite3 import Connection
from app.db.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get("/me")
def get_my_profile(db: Connection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cursor = db.cursor()

    cursor.execute(
        "SELECT id, email, name, role, is_email_verified, created_at FROM users WHERE id = ?",
        (current_user["id"],)
    )
    user = dict(cursor.fetchone())

    cursor.execute(
        "SELECT id, title, slug, downloads, rating, is_active FROM systems WHERE owner_id = ? ORDER BY created_at DESC",
        (current_user["id"],)
    )
    my_systems = [dict(r) for r in cursor.fetchall()]

    cursor.execute(
        """SELECT r.id, r.rating, r.comment, r.created_at, s.title as system_title, s.slug as system_slug
           FROM reviews r JOIN systems s ON r.system_id = s.id
           WHERE r.user_id = ? ORDER BY r.created_at DESC""",
        (current_user["id"],)
    )
    my_reviews = [dict(r) for r in cursor.fetchall()]

    total_downloads_received = sum(s["downloads"] for s in my_systems)

    return {
        "user": user,
        "my_systems": my_systems,
        "my_reviews": my_reviews,
        "total_downloads_received": total_downloads_received
    }
