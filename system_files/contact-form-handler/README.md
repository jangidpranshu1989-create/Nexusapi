# Contact Form Handler API

Receives contact form submissions, stores them, and optionally sends an email notification.

## Features
- Validates name, email, message
- Stores every submission in SQLite
- Optional email notification via Gmail SMTP (works fine without it configured)

## Setup

pip install fastapi uvicorn pydantic[email]
uvicorn main:app --reload

## Enabling email notifications (optional)

export NOTIFY_EMAIL="you@example.com"
export SMTP_ADDRESS="your-gmail@gmail.com"
export SMTP_APP_PASSWORD="your-16-char-gmail-app-password"

Without these set, the API still works and just skips sending email.

## Usage

Submit the form:
curl -X POST http://localhost:8000/contact -H "Content-Type: application/json" -d '{"name": "Ravi Kumar", "email": "ravi@example.com", "message": "I have a question about pricing."}'

List submissions:
curl http://localhost:8000/submissions

Get one:
curl http://localhost:8000/submissions/1

## Notes
- /submissions has no authentication in this starter version — add admin auth before deploying publicly.
- Gmail requires an App Password (not your normal password) for SMTP.
