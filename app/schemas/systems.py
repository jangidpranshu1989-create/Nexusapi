from pydantic import BaseModel
from typing import Optional

class SystemCreate(BaseModel):
    title: str
    slug: str
    category: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    setup_time: Optional[int] = None
    complexity: Optional[str] = None

class SystemUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    setup_time: Optional[int] = None
    complexity: Optional[str] = None

class SystemResponse(BaseModel):
    id: int
    title: str
    slug: str
    category: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    setup_time: Optional[int] = None
    complexity: Optional[str] = None
    downloads: int
    rating: float
    is_active: bool
    created_at: str
