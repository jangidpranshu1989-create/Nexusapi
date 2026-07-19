"""
Password Strength Checker API
Endpoint:
  POST /check-strength   - analyze a password, return score + feedback
Stateless — no password is ever stored.
Run with:  uvicorn main:app --reload
"""

import re
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Password Strength Checker API")


class PasswordCheckRequest(BaseModel):
    password: str


class PasswordCheckResponse(BaseModel):
    score: int
    strength: str
    feedback: list[str]
    length: int


COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "password1",
    "111111", "123123", "letmein", "welcome", "admin", "iloveyou",
    "monkey", "dragon", "sunshine", "princess", "football"
}


def check_password_strength(password: str) -> PasswordCheckResponse:
    feedback = []
    score = 0
    length = len(password)

    if length >= 12:
        score += 40
    elif length >= 8:
        score += 25
        feedback.append("Consider using 12 or more characters for stronger security.")
    elif length >= 6:
        score += 10
        feedback.append("Password is quite short — use at least 8 characters, ideally 12+.")
    else:
        feedback.append("Password is too short — use at least 8 characters.")

    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_symbol = bool(re.search(r"[^a-zA-Z0-9]", password))

    if has_lower:
        score += 10
    else:
        feedback.append("Add lowercase letters.")
    if has_upper:
        score += 10
    else:
        feedback.append("Add uppercase letters.")
    if has_digit:
        score += 10
    else:
        feedback.append("Add numbers.")
    if has_symbol:
        score += 10
    else:
        feedback.append("Add special characters (e.g. !@#$%).")

    if password.lower() in COMMON_PASSWORDS:
        score = max(0, score - 50)
        feedback.append("This is a commonly used password — choose something more unique.")
    elif score >= 60:
        score = min(100, score + 20)

    if re.search(r"(.)\1{2,}", password):
        score = max(0, score - 15)
        feedback.append("Avoid repeating the same character multiple times in a row.")

    score = max(0, min(100, score))

    if score < 20:
        strength = "very weak"
    elif score < 40:
        strength = "weak"
    elif score < 60:
        strength = "moderate"
    elif score < 80:
        strength = "strong"
    else:
        strength = "very strong"

    if not feedback:
        feedback.append("Great password! No issues found.")

    return PasswordCheckResponse(score=score, strength=strength, feedback=feedback, length=length)


@app.post("/check-strength", response_model=PasswordCheckResponse)
def check_strength(payload: PasswordCheckRequest):
    return check_password_strength(payload.password)
