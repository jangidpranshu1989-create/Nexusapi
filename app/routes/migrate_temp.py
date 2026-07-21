"""
TEMPORARY endpoint to run the settings migration on production.
DELETE after use.
"""

import os
import sqlite3
from fastapi import APIRouter, HTTPException
from app.db.database import get_db

router = APIRouter()

MIGRATE_SECRET = os.getenv("SETUP_SECRET", "")


@router.post("/run-settings-migration")
def run_migration(secret: str):
    if not MIGRATE_SECRET or secret != MIGRATE_SECRET:
        raise HTTPException(403, "Invalid secret")

    conn = sqlite3.connect(os.getenv("DB_PATH", "nexus.db"))
    cursor = conn.cursor()
    results = []

    for col, coltype in [("bio", "TEXT"), ("accent_color", "TEXT DEFAULT '#6C5CE7'"), ("email_notifications", "INTEGER DEFAULT 1")]:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {coltype}")
            results.append(f"Added {col}")
        except sqlite3.OperationalError:
            results.append(f"{col} already exists")

    conn.commit()
    conn.close()
    return {"results": results}
