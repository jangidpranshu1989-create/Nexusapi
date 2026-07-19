from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import Connection
from typing import List
from pydantic import BaseModel
from app.db.database import get_db
from app.core.dependencies import require_admin

router = APIRouter()


def log_action(db, admin, action, target_type, target_id, details=""):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (admin_id, admin_email, action, target_type, target_id, details) VALUES (?, ?, ?, ?, ?, ?)",
        (admin["id"], admin["email"], action, target_type, target_id, details)
    )
    db.commit()


@router.get("/stats")
def get_stats(db: Connection = Depends(get_db), admin: dict = Depends(require_admin)):
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM systems")
    systems = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(downloads),0) FROM systems")
    downloads = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM reviews")
    reviews = c.fetchone()[0]
    return {"total_users": users, "total_systems": systems, "total_downloads": downloads, "total_reviews": reviews}


@router.get("/users")
def list_users(page: int = Query(1, ge=1), db: Connection = Depends(get_db), admin: dict = Depends(require_admin)):
    size = 20
    offset = (page - 1) * size
    c = db.cursor()
    c.execute("SELECT id, email, name, role, is_email_verified, created_at FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?", (size, offset))
    rows = [dict(r) for r in c.fetchall()]
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    return {"items": rows, "page": page, "total": total}


@router.put("/users/{user_id}/role")
def update_role(user_id: int, role: str, db: Connection = Depends(get_db), admin: dict = Depends(require_admin)):
    if role not in {"user", "developer", "admin"}:
        raise HTTPException(400, "Invalid role")
    c = db.cursor()
    c.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if not c.fetchone():
        raise HTTPException(404, "User not found")
    c.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    db.commit()
    log_action(db, admin, "update_role", "user", user_id, f"role={role}")
    return {"message": f"Role updated to {role}"}


@router.get("/systems")
def list_systems(page: int = Query(1, ge=1), db: Connection = Depends(get_db), admin: dict = Depends(require_admin)):
    size = 20
    offset = (page - 1) * size
    c = db.cursor()
    c.execute("""SELECT s.id,s.title,s.slug,s.category,s.is_active,s.downloads,s.owner_id,u.email as owner_email
                 FROM systems s LEFT JOIN users u ON s.owner_id=u.id
                 ORDER BY s.created_at DESC LIMIT ? OFFSET ?""", (size, offset))
    rows = [dict(r) for r in c.fetchall()]
    c.execute("SELECT COUNT(*) FROM systems")
    total = c.fetchone()[0]
    return {"items": rows, "page": page, "total": total}


class BulkAction(BaseModel):
    system_ids: List[int]
    active: bool


@router.put("/systems/bulk-toggle")
def bulk_toggle(payload: BulkAction, db: Connection = Depends(get_db), admin: dict = Depends(require_admin)):
    c = db.cursor()
    for sid in payload.system_ids:
        c.execute("UPDATE systems SET is_active=? WHERE id=?", (int(payload.active), sid))
    db.commit()
    log_action(db, admin, "bulk_toggle", "system", None, f"ids={payload.system_ids} active={payload.active}")
    return {"message": f"Updated {len(payload.system_ids)} systems"}


@router.get("/audit-logs")
def get_logs(page: int = Query(1, ge=1), db: Connection = Depends(get_db), admin: dict = Depends(require_admin)):
    size = 30
    offset = (page - 1) * size
    c = db.cursor()
    c.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ? OFFSET ?", (size, offset))
    rows = [dict(r) for r in c.fetchall()]
    c.execute("SELECT COUNT(*) FROM audit_logs")
    total = c.fetchone()[0]
    return {"items": rows, "page": page, "total": total}
