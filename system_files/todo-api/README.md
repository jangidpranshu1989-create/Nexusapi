# Todo / Task Manager API

Simple task management backend with FastAPI and SQLite.

## Features
- Create, read, update, delete todos
- Optional due dates
- Filter by completion status

## Setup

pip install fastapi uvicorn
uvicorn main:app --reload

## Usage

Create a todo:
curl -X POST http://localhost:8000/todos -H "Content-Type: application/json" -d '{"title": "Buy groceries", "due_date": "2026-07-20"}'

List todos:
curl http://localhost:8000/todos

Filter completed:
curl "http://localhost:8000/todos?completed=true"

Update (mark complete):
curl -X PUT http://localhost:8000/todos/1 -H "Content-Type: application/json" -d '{"completed": true}'

Delete:
curl -X DELETE http://localhost:8000/todos/1

## Notes
- due_date accepts ISO format (YYYY-MM-DD)
- PUT is partial — only send fields you want to change
