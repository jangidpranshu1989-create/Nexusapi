# Webhook Logger API

Captures any incoming webhook (Stripe, GitHub, Slack, or custom), stores headers and body, lets you inspect later.

## Features
- Accepts webhooks at any /webhook/{source} path
- Stores raw headers and body exactly as received
- List and filter by source

## Setup

pip install fastapi uvicorn
uvicorn main:app --reload

## Usage

Point any webhook sender at:
POST http://localhost:8000/webhook/stripe
POST http://localhost:8000/webhook/github

Simulate manually:
curl -X POST http://localhost:8000/webhook/stripe -H "Content-Type: application/json" -d '{"event": "payment.succeeded", "amount": 500}'

List captured webhooks:
curl http://localhost:8000/webhooks
curl "http://localhost:8000/webhooks?source=stripe"

View full details:
curl http://localhost:8000/webhooks/1

## Notes
- Meant for development/debugging — no signature verification included.
- Use ngrok to expose this locally-running logger to the internet for real third-party testing.
