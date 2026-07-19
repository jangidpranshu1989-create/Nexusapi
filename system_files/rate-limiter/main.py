"""
Rate Limiter Middleware
A reusable, self-contained IP-based rate limiter for FastAPI using the
sliding-window-counter approach, stored in memory.

Endpoints (demo):
  GET /  - a sample protected endpoint, rate-limited to N requests per window
Run with:  uvicorn main:app --reload
"""

import time
from collections import defaultdict, deque
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

MAX_REQUESTS = 5
WINDOW_SECONDS = 60

request_log: dict = defaultdict(deque)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        timestamps = request_log[client_ip]

        while timestamps and now - timestamps[0] > WINDOW_SECONDS:
            timestamps.popleft()

        if len(timestamps) >= MAX_REQUESTS:
            retry_after = WINDOW_SECONDS - (now - timestamps[0])
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Try again in {retry_after:.1f} seconds.",
                    "limit": MAX_REQUESTS,
                    "window_seconds": WINDOW_SECONDS
                },
                headers={"Retry-After": str(int(retry_after) + 1)}
            )

        timestamps.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(MAX_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(MAX_REQUESTS - len(timestamps))
        return response


app = FastAPI(title="Rate Limiter Demo")
app.add_middleware(RateLimitMiddleware)


@app.get("/")
def protected_endpoint():
    return {"message": f"Request allowed. Limit is {MAX_REQUESTS} requests per {WINDOW_SECONDS} seconds."}
