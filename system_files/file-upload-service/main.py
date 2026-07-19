"""
File Upload Service API
Endpoints:
  POST   /upload              - upload a file (multipart/form-data)
  GET    /files                - list uploaded files (metadata only)
  GET    /files/{id}           - get metadata for one file
  GET    /files/{id}/download  - download the actual file
  DELETE /files/{id}           - delete a file
Run with:  uvicorn main:app --reload
"""

import os
import sqlite3
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="File Upload Service API")
DB_PATH = "file_uploads.db"
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".zip", ".docx", ".csv"}

os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL UNIQUE,
            size_bytes INTEGER NOT NULL,
            content_type TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


class FileMetadata(BaseModel):
    id: int
    original_filename: str
    size_bytes: int
    content_type: str | None
    uploaded_at: str


def validate_extension(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    return ext


@app.post("/upload", response_model=FileMetadata, status_code=201)
async def upload_file(file: UploadFile = File(...)):
    ext = validate_extension(file.filename)
    contents = await file.read()
    size_bytes = len(contents)

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max is {MAX_FILE_SIZE_MB}MB")

    stored_filename = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(UPLOAD_DIR, stored_filename)
    with open(stored_path, "wb") as f:
        f.write(contents)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO files (original_filename, stored_filename, size_bytes, content_type) VALUES (?, ?, ?, ?)",
        (file.filename, stored_filename, size_bytes, file.content_type)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM files WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()

    return FileMetadata(id=row["id"], original_filename=row["original_filename"], size_bytes=row["size_bytes"], content_type=row["content_type"], uploaded_at=row["uploaded_at"])


@app.get("/files", response_model=list[FileMetadata])
def list_files():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files ORDER BY uploaded_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [FileMetadata(id=r["id"], original_filename=r["original_filename"], size_bytes=r["size_bytes"], content_type=r["content_type"], uploaded_at=r["uploaded_at"]) for r in rows]


@app.get("/files/{file_id}", response_model=FileMetadata)
def get_file_metadata(file_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="File not found")
    return FileMetadata(id=row["id"], original_filename=row["original_filename"], size_bytes=row["size_bytes"], content_type=row["content_type"], uploaded_at=row["uploaded_at"])


@app.get("/files/{file_id}/download")
def download_file(file_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="File not found")
    stored_path = os.path.join(UPLOAD_DIR, row["stored_filename"])
    if not os.path.exists(stored_path):
        raise HTTPException(status_code=404, detail="File exists in database but not on disk")
    return FileResponse(stored_path, filename=row["original_filename"], media_type=row["content_type"] or "application/octet-stream")


@app.delete("/files/{file_id}", status_code=204)
def delete_file(file_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="File not found")
    stored_path = os.path.join(UPLOAD_DIR, row["stored_filename"])
    if os.path.exists(stored_path):
        os.remove(stored_path)
    cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
    conn.commit()
    conn.close()
    return None
