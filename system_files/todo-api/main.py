"""
Todo / Task Manager API
Endpoints:
  POST   /todos       - create a new todo
  GET    /todos        - list todos (optional ?completed=true/false)
  GET    /todos/{id}   - get a single todo
  PUT    /todos/{id}   - update a todo
  DELETE /todos/{id}   - delete a todo
Run with:  uvicorn main:app --reload
"""

import sqlite3
from datetime import date
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="Todo API")
DB_PATH = "todos.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


class TodoCreate(BaseModel):
    title: str
    due_date: Optional[date] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    due_date: Optional[str]
    completed: bool
    created_at: str


def row_to_response(row):
    return TodoResponse(
        id=row["id"], title=row["title"], due_date=row["due_date"],
        completed=bool(row["completed"]), created_at=row["created_at"]
    )


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(payload: TodoCreate):
    conn = get_db()
    cursor = conn.cursor()
    due = payload.due_date.isoformat() if payload.due_date else None
    cursor.execute("INSERT INTO todos (title, due_date) VALUES (?, ?)", (payload.title, due))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM todos WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()
    return row_to_response(row)


@app.get("/todos", response_model=list[TodoResponse])
def list_todos(completed: Optional[bool] = Query(None)):
    conn = get_db()
    cursor = conn.cursor()
    if completed is None:
        cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
    else:
        cursor.execute("SELECT * FROM todos WHERE completed = ? ORDER BY created_at DESC", (1 if completed else 0,))
    rows = cursor.fetchall()
    conn.close()
    return [row_to_response(r) for r in rows]


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Todo not found")
    return row_to_response(row)


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, payload: TodoUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    new_title = payload.title if payload.title is not None else row["title"]
    new_due = payload.due_date.isoformat() if payload.due_date is not None else row["due_date"]
    new_completed = int(payload.completed) if payload.completed is not None else row["completed"]

    cursor.execute(
        "UPDATE todos SET title = ?, due_date = ?, completed = ? WHERE id = ?",
        (new_title, new_due, new_completed, todo_id)
    )
    conn.commit()
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    updated = cursor.fetchone()
    conn.close()
    return row_to_response(updated)


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return None
