from pydantic import BaseModel, Field
from typing import Optional

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    system_id: int
    user_id: int
    user_name: str
    rating: int
    comment: Optional[str] = None
    created_at: str
