"""
Webhook Logger API
Endpoints:
  POST /webhook/{source}   - receive and store a webhook
  GET  /webhooks             - list all captured webhooks (optional ?source=X)
  GET  /webhooks/{id}        - view full details of one webhook
  DELETE /webhooks/{id}      - delete a webhook
Run with:  uvicorn main:app --reload
"""

import sqlite3
import json
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Query
from pydantic import BaseModel

app = FastAPI(title="Webhook Logger API")
DB_PATH = "webhooks.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS webhooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            method TEXT NOT NULL,
            headers TEXT NOT NULL,
            body TEXT,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


class WebhookSummary(BaseModel):
    id: int
    source: str
    method: str
    received_at: str


class WebhookDetail(BaseModel):
    id: int
    source: str
    method: str
    headers: dict
    body: Optional[str]
    received_at: str


@app.post("/webhook/{source}")
async def receive_webhook(source: str, request: Request):
    body_bytes = await request.body()
    try:
        body_str = body_bytes.decode("utf-8")
    except UnicodeDecodeError:
        body_str = "<binary data, could not decode as UTF-8>"

    headers_dict = dict(request.headers)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO webhooks (source, method, headers, body) VALUES (?, ?, ?, ?)",
        (source, request.method, json.dumps(headers_dict), body_str)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"status": "received", "id": new_id, "source": source}


@app.get("/webhooks", response_model=list[WebhookSummary])
def list_webhooks(source: Optional[str] = Query(None)):
    conn = get_db()
    cursor = conn.cursor()
    if source:
        cursor.execute(
            "SELECT id, source, method, received_at FROM webhooks WHERE source = ? ORDER BY received_at DESC",
            (source,)
        )
    else:
        cursor.execute("SELECT id, source, method, received_at FROM webhooks ORDER BY received_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        WebhookSummary(id=r["id"], source=r["source"], method=r["method"], received_at=r["received_at"])
        for r in rows
    ]


@app.get("/webhooks/{webhook_id}", response_model=WebhookDetail)
def get_webhook(webhook_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM webhooks WHERE id = ?", (webhook_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return WebhookDetail(
        id=row["id"], source=row["source"], method=row["method"],
        headers=json.loads(row["headers"]), body=row["body"], received_at=row["received_at"]
    )


@app.delete("/webhooks/{webhook_id}", status_code=204)
def delete_webhook(webhook_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM webhooks WHERE id = ?", (webhook_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Webhook not found")
    cursor.execute("DELETE FROM webhooks WHERE id = ?", (webhook_id,))
    conn.commit()
    conn.close()
    return None
