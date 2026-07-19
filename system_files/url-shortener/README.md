# URL Shortener API

A minimal, self-contained URL shortening service built with FastAPI and SQLite.

## Features
- Shorten any valid URL into a 6-character code
- Automatic redirect from short code to original URL
- Click tracking per short link
- Stats endpoint to check click count without redirecting

## Setup

pip install fastapi uvicorn
uvicorn main:app --reload

Server runs at http://localhost:8000

## Usage

Create a short link:

curl -X POST http://localhost:8000/shorten -H "Content-Type: application/json" -d '{"url": "https://example.com/some/very/long/path"}'

Response will include a code, short_url, and original_url.

Use the short link by visiting http://localhost:8000/aB3xY9 in a browser — it redirects to the original URL.

Check stats:

curl http://localhost:8000/stats/aB3xY9

## Notes
- Uses SQLite (shortener.db), created automatically on first run — zero external database setup needed.
- Codes are 6 characters (letters + digits), collision-checked on creation.
- For production use, consider adding rate limiting and a custom domain for short links.
