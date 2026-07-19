"""
Contact Form Handler API
Endpoints:
  POST /contact          - submit a contact form message
  GET  /submissions       - list all submissions
  GET  /submissions/{id}  - view a single submission
Run with:  uvicorn main:app --reload
"""

import os
import sqlite3
import smtplib
from email.message import EmailMessage
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Contact Form Handler API")
DB_PATH = "contact_submissions.db"

NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")
SMTP_ADDRESS = os.getenv("SMTP_ADDRESS")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


class ContactSubmission(BaseModel):
    name: str
    email: EmailStr
    message: str


class SubmissionResponse(BaseModel):
    id: int
    name: str
    email: str
    message: str
    created_at: str


def try_send_notification(name, email, message):
    if not (NOTIFY_EMAIL and SMTP_ADDRESS and SMTP_APP_PASSWORD):
        return
    try:
        msg = EmailMessage()
        msg["Subject"] = f"New contact form submission from {name}"
        msg["From"] = SMTP_ADDRESS
        msg["To"] = NOTIFY_EMAIL
        msg.set_content(f"From: {name} <{email}>\n\nMessage:\n{message}")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_ADDRESS, SMTP_APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"WARNING: failed to send notification email: {e}")


@app.post("/contact", response_model=SubmissionResponse, status_code=201)
def submit_contact_form(payload: ContactSubmission):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO submissions (name, email, message) VALUES (?, ?, ?)",
        (payload.name, payload.email, payload.message)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM submissions WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()
    try_send_notification(payload.name, payload.email, payload.message)
    return SubmissionResponse(
        id=row["id"], name=row["name"], email=row["email"],
        message=row["message"], created_at=row["created_at"]
    )


@app.get("/submissions", response_model=list[SubmissionResponse])
def list_submissions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM submissions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        SubmissionResponse(id=r["id"], name=r["name"], email=r["email"], message=r["message"], created_at=r["created_at"])
        for r in rows
    ]


@app.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Submission not found")
    return SubmissionResponse(
        id=row["id"], name=row["name"], email=row["email"], message=row["message"], created_at=row["created_at"]
    )
