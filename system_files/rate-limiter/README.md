# Rate Limiter Middleware

A reusable, in-memory, IP-based rate limiter for FastAPI using the sliding window algorithm. No Redis needed.

## Features
- Per-IP request limiting (default: 5 requests per 60 seconds, configurable)
- Sliding window algorithm (more accurate than fixed-window)
- Adds X-RateLimit-Limit / X-RateLimit-Remaining headers
- Returns proper 429 with Retry-After header when exceeded

## Setup

pip install fastapi uvicorn
uvicorn main:app --reload

## Usage

Try hitting the endpoint more than 5 times within 60 seconds:
for i in 1 2 3 4 5 6; do curl -i http://localhost:8000/; echo; done

First 5 succeed, 6th returns 429.

## Using this in your own project

Copy the RateLimitMiddleware class and request_log dict into your app, then add:
app.add_middleware(RateLimitMiddleware)

Adjust MAX_REQUESTS and WINDOW_SECONDS at the top of the file.

## Notes
- In-memory — limits reset on server restart, and does not work correctly across multiple server instances behind a load balancer. Use Redis for multi-instance setups.
