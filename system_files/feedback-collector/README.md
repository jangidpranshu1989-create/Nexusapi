# Feedback/NPS Collector API

Collects Net Promoter Score (0-10) ratings with optional comments, calculates overall NPS.

## Setup
pip install fastapi uvicorn
uvicorn main:app --reload

## Usage

Submit: curl -X POST http://localhost:8000/feedback -H "Content-Type: application/json" -d '{"score": 9, "comment": "Great product!"}'
List: curl http://localhost:8000/feedback
Stats: curl http://localhost:8000/feedback/stats

## Notes
- NPS = % Promoters (score 9-10) minus % Detractors (score 0-6). Passives (7-8) are counted but don't affect the score.
