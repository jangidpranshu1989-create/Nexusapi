# Password Strength Checker API

Analyzes a password and returns a strength score (0-100), label, and specific feedback. Stateless — nothing is stored.

## Setup
pip install fastapi uvicorn
uvicorn main:app --reload

## Usage

Check weak password: curl -X POST http://localhost:8000/check-strength -H "Content-Type: application/json" -d '{"password": "password123"}'
Check strong password: curl -X POST http://localhost:8000/check-strength -H "Content-Type: application/json" -d '{"password": "Xk9#mP2$vL7q"}'

## Notes
- Password is never stored or logged — analyzed in-memory only.
- Checks length, character variety, common-password list, and repeated characters.
