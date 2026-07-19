#!/bin/bash
set -a
source .env 2>/dev/null || true
set +a

PORT=${PORT:-8000}

uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
