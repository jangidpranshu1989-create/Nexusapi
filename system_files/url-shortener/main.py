"""
URL Shortener API
A simple, self-contained URL shortening service built with FastAPI + SQLite.

Endpoints:
  POST /shorten       - create a short link from a long URL
  GET  /{code}        - redirect to the original URL (and count the click)
  GET  /stats/{code}  - view click count and original URL for a short code

Run with:  uvicorn main:app --reload
"""

import sqlite3
import string
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="URL Shortener API")

DB_PATH = "shortener.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS links (
            code TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


def generate_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    original_url: str


@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(payload: ShortenRequest):
    conn = get_db()
    cursor = conn.cursor()

    for _ in range(5):
        code = generate_code()
        cursor.execute("SELECT code FROM links WHERE code = ?", (code,))
        if not cursor.fetchone():
            break
    else:
        conn.close()
        raise HTTPException(status_code=500, detail="Could not generate a unique code, try again")

    cursor.execute(
        "INSERT INTO links (code, original_url) VALUES (?, ?)",
        (code, str(payload.url))
    )
    conn.commit()
    conn.close()

    return ShortenResponse(
        code=code,
        short_url=f"/{code}",
        original_url=str(payload.url)
    )


@app.get("/stats/{code}")
def get_stats(code: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM links WHERE code = ?", (code,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Short code not found")

    return {
        "code": row["code"],
        "original_url": row["original_url"],
        "clicks": row["clicks"],
        "created_at": row["created_at"]
    }


@app.get("/{code}")
def redirect_to_original(code: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT original_url FROM links WHERE code = ?", (code,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Short code not found")

    cursor.execute("UPDATE links SET clicks = clicks + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()

    return RedirectResponse(url=row["original_url"])
