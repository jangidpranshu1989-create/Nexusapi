"""
QR Code Generator API
Endpoints:
  GET  /qr?data=...   - generate and return a QR code PNG directly
  POST /qr/save        - generate, store, and return an ID + retrieval URL
  GET  /qr/{id}        - retrieve a previously saved QR code image
Run with:  uvicorn main:app --reload
"""

import sqlite3
import io
import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import qrcode

app = FastAPI(title="QR Code Generator API")
DB_PATH = "qr_codes.db"
STORAGE_DIR = "qr_images"
os.makedirs(STORAGE_DIR, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS qr_codes (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            filename TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


class SaveQRRequest(BaseModel):
    data: str


class SaveQRResponse(BaseModel):
    id: str
    data: str
    retrieval_url: str


def generate_qr_image_bytes(data: str) -> bytes:
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


@app.get("/qr")
def generate_qr_direct(data: str):
    if not data or not data.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'data' must not be empty")
    image_bytes = generate_qr_image_bytes(data)
    return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")


@app.post("/qr/save", response_model=SaveQRResponse, status_code=201)
def generate_and_save_qr(payload: SaveQRRequest):
    if not payload.data.strip():
        raise HTTPException(status_code=400, detail="'data' must not be empty")

    qr_id = uuid.uuid4().hex[:10]
    filename = f"{qr_id}.png"
    filepath = os.path.join(STORAGE_DIR, filename)
    image_bytes = generate_qr_image_bytes(payload.data)
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO qr_codes (id, data, filename) VALUES (?, ?, ?)", (qr_id, payload.data, filename))
    conn.commit()
    conn.close()

    return SaveQRResponse(id=qr_id, data=payload.data, retrieval_url=f"/qr/{qr_id}")


@app.get("/qr/{qr_id}")
def get_saved_qr(qr_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM qr_codes WHERE id = ?", (qr_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="QR code not found")
    filepath = os.path.join(STORAGE_DIR, row["filename"])
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="QR image file missing on disk")
    return FileResponse(filepath, media_type="image/png")
