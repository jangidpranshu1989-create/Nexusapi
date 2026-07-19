from pydantic import BaseModel, Field
from typing import Optional

class UserRegister(BaseModel):
    email: str = Field(..., pattern=r"^\S+@\S+\.\S+$")
    password: str
    name: str

class UserLogin(BaseModel):
    email: str = Field(..., pattern=r"^\S+@\S+\.\S+$")
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    avatar_url: Optional[str] = None
    created_at: str
