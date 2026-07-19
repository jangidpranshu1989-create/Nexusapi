"""
Blog/CMS API
Endpoints:
  POST   /posts        - create a post (defaults to draft)
  GET    /posts         - list posts (optional ?status=X, ?tag=X)
  GET    /posts/{slug}  - get a single post
  PUT    /posts/{slug}  - update a post
  DELETE /posts/{slug}  - delete a post
Run with:  uvicorn main:app --reload
"""

import sqlite3
import re
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="Blog/CMS API")
DB_PATH = "blog.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL,
            tags TEXT,
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


def slugify(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    return slug


class PostCreate(BaseModel):
    title: str
    content: str
    tags: Optional[str] = None
    status: str = "draft"


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    tags: Optional[str]
    status: str
    created_at: str
    updated_at: str


def row_to_response(row):
    return PostResponse(id=row["id"], title=row["title"], slug=row["slug"], content=row["content"], tags=row["tags"], status=row["status"], created_at=row["created_at"], updated_at=row["updated_at"])


VALID_STATUSES = {"draft", "published"}


@app.post("/posts", response_model=PostResponse, status_code=201)
def create_post(payload: PostCreate):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {VALID_STATUSES}")

    conn = get_db()
    cursor = conn.cursor()
    base_slug = slugify(payload.title)
    slug = base_slug
    suffix = 1
    while True:
        cursor.execute("SELECT id FROM posts WHERE slug = ?", (slug,))
        if not cursor.fetchone():
            break
        suffix += 1
        slug = f"{base_slug}-{suffix}"

    cursor.execute("INSERT INTO posts (title, slug, content, tags, status) VALUES (?, ?, ?, ?, ?)", (payload.title, slug, payload.content, payload.tags, payload.status))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM posts WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()
    return row_to_response(row)


@app.get("/posts", response_model=list[PostResponse])
def list_posts(status: Optional[str] = Query(None), tag: Optional[str] = Query(None)):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM posts WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if tag:
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")
    query += " ORDER BY created_at DESC"
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [row_to_response(r) for r in rows]


@app.get("/posts/{slug}", response_model=PostResponse)
def get_post(slug: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    return row_to_response(row)


@app.put("/posts/{slug}", response_model=PostResponse)
def update_post(slug: str, payload: PostUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Post not found")
    if payload.status is not None and payload.status not in VALID_STATUSES:
        conn.close()
        raise HTTPException(status_code=400, detail=f"status must be one of {VALID_STATUSES}")

    new_title = payload.title if payload.title is not None else row["title"]
    new_content = payload.content if payload.content is not None else row["content"]
    new_tags = payload.tags if payload.tags is not None else row["tags"]
    new_status = payload.status if payload.status is not None else row["status"]

    cursor.execute("UPDATE posts SET title = ?, content = ?, tags = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE slug = ?", (new_title, new_content, new_tags, new_status, slug))
    conn.commit()
    cursor.execute("SELECT * FROM posts WHERE slug = ?", (slug,))
    updated = cursor.fetchone()
    conn.close()
    return row_to_response(updated)


@app.delete("/posts/{slug}", status_code=204)
def delete_post(slug: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM posts WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Post not found")
    cursor.execute("DELETE FROM posts WHERE slug = ?", (slug,))
    conn.commit()
    conn.close()
    return None
