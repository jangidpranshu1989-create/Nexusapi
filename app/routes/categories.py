from fastapi import APIRouter, Depends, HTTPException, status
from sqlite3 import Connection
from typing import List
from app.db.database import get_db
from app.schemas.categories import CategoryCreate, CategoryResponse
from app.core.dependencies import require_admin

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
def list_categories(db: Connection = Depends(get_db)):
    cursor = db.cursor()
    
    query = """
        SELECT c.id, c.name, c.slug, c.icon,
               (SELECT COUNT(*) FROM systems s WHERE s.category = c.slug AND s.is_active = 1) as count
        FROM categories c
        ORDER BY c.name ASC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    
    return [dict(row) for row in rows]

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Connection = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM categories WHERE slug = ?", (category.slug,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Category slug already exists")
        
    cursor.execute(
        "INSERT INTO categories (name, slug, icon, count) VALUES (?, ?, ?, 0)",
        (category.name, category.slug, category.icon)
    )
    db.commit()
    new_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM categories WHERE id = ?", (new_id,))
    res = dict(cursor.fetchone())
    res["count"] = 0
    
    return res
