from pydantic import BaseModel
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    slug: str
    icon: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str] = None
    count: int
