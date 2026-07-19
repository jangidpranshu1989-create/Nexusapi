"""
Feedback / NPS Collector API
Endpoints:
  POST /feedback        - submit feedback (score 0-10 + optional comment)
  GET  /feedback         - list all feedback
  GET  /feedback/stats   - calculate NPS and breakdown
Run with:  uvicorn main:app --reload
"""

import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Feedback/NPS Collector API")
DB_PATH = "feedback.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


class FeedbackCreate(BaseModel):
    score: int = Field(..., ge=0, le=10)
    comment: str | None = None


class FeedbackResponse(BaseModel):
    id: int
    score: int
    comment: str | None
    created_at: str


class NPSStats(BaseModel):
    total_responses: int
    promoters: int
    passives: int
    detractors: int
    nps_score: float


def classify(score: int) -> str:
    if score >= 9:
        return "promoter"
    elif score >= 7:
        return "passive"
    return "detractor"


@app.post("/feedback", response_model=FeedbackResponse, status_code=201)
def submit_feedback(payload: FeedbackCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedback (score, comment) VALUES (?, ?)", (payload.score, payload.comment))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM feedback WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()
    return FeedbackResponse(id=row["id"], score=row["score"], comment=row["comment"], created_at=row["created_at"])


@app.get("/feedback", response_model=list[FeedbackResponse])
def list_feedback():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [FeedbackResponse(id=r["id"], score=r["score"], comment=r["comment"], created_at=r["created_at"]) for r in rows]


@app.get("/feedback/stats", response_model=NPSStats)
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM feedback")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return NPSStats(total_responses=0, promoters=0, passives=0, detractors=0, nps_score=0.0)

    scores = [r["score"] for r in rows]
    total = len(scores)
    promoters = sum(1 for s in scores if classify(s) == "promoter")
    passives = sum(1 for s in scores if classify(s) == "passive")
    detractors = sum(1 for s in scores if classify(s) == "detractor")
    nps = round((promoters / total * 100) - (detractors / total * 100), 1)

    return NPSStats(total_responses=total, promoters=promoters, passives=passives, detractors=detractors, nps_score=nps)
