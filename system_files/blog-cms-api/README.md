# Blog/CMS API

Minimal content management backend for blog posts with draft/published status and tags.

## Setup
pip install fastapi uvicorn
uvicorn main:app --reload

## Usage

Create: curl -X POST http://localhost:8000/posts -H "Content-Type: application/json" -d '{"title": "My First Post", "content": "Hello world!", "tags": "intro", "status": "published"}'
List published: curl "http://localhost:8000/posts?status=published"
Filter by tag: curl "http://localhost:8000/posts?tag=intro"
Update: curl -X PUT http://localhost:8000/posts/my-first-post -H "Content-Type: application/json" -d '{"status": "draft"}'
Delete: curl -X DELETE http://localhost:8000/posts/my-first-post

## Notes
- Slugs auto-generate and auto-dedupe on collision.
- No authentication — add auth before public post creation.
