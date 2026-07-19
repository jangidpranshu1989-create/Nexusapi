from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlite3 import Connection
from typing import Optional
from app.db.database import get_db
from app.schemas.systems import SystemCreate, SystemUpdate, SystemResponse
from app.core.dependencies import require_developer_or_admin

router = APIRouter()

@router.get("/", response_model=dict)
def list_systems(
    category: Optional[str] = None,
    sort: str = Query("newest", pattern="^(newest|downloads|rating)$"),
    page: int = Query(1, ge=1),
    db: Connection = Depends(get_db)
):
    page_size = 20
    offset = (page - 1) * page_size
    cursor = db.cursor()
    
    query = "SELECT * FROM systems WHERE is_active = 1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
        
    if sort == "newest":
        query += " ORDER BY created_at DESC"
    elif sort == "downloads":
        query += " ORDER BY downloads DESC"
    elif sort == "rating":
        query += " ORDER BY rating DESC"
        
    query += " LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    
    cursor.execute(query, tuple(params))
    items = [dict(row) for row in cursor.fetchall()]
    
    count_query = "SELECT COUNT(*) FROM systems WHERE is_active = 1"
    count_params = []
    if category:
        count_query += " AND category = ?"
        count_params.append(category)
        
    cursor.execute(count_query, tuple(count_params))
    total = cursor.fetchone()[0]
    
    return {"items": items, "page": page, "total": total}

@router.get("/{slug}", response_model=SystemResponse)
def get_system(slug: str, db: Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM systems WHERE slug = ? AND is_active = 1", (slug,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="System not found")
        
    return dict(row)

@router.post("/", response_model=SystemResponse, status_code=status.HTTP_201_CREATED)
def create_system(
    system: SystemCreate, 
    db: Connection = Depends(get_db), 
    current_user: dict = Depends(require_developer_or_admin)
):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM systems WHERE slug = ?", (system.slug,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Slug already exists")
        
    cursor.execute(
        """INSERT INTO systems 
        (title, slug, category, description, tech_stack, setup_time, complexity, downloads, rating, is_active, owner_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0.0, 1, ?)""",
        (system.title, system.slug, system.category, system.description, system.tech_stack, system.setup_time, system.complexity, current_user["id"])
    )
    db.commit()
    new_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM systems WHERE id = ?", (new_id,))
    return dict(cursor.fetchone())

@router.put("/{slug}", response_model=SystemResponse)
def update_system(
    slug: str, 
    system_update: SystemUpdate, 
    db: Connection = Depends(get_db), 
    current_user: dict = Depends(require_developer_or_admin)
):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM systems WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="System not found")
        
    if current_user["role"] != "admin" and row["owner_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own systems"
        )
        
    update_data = system_update.dict(exclude_unset=True)
    if not update_data:
        return dict(row)
        
    set_clauses = []
    params = []
    for key, value in update_data.items():
        set_clauses.append(f"{key} = ?")
        params.append(value)
        
    params.append(slug)
    
    query = f"UPDATE systems SET {', '.join(set_clauses)} WHERE slug = ?"
    cursor.execute(query, tuple(params))
    db.commit()
    
    new_slug = update_data.get("slug", slug)
    cursor.execute("SELECT * FROM systems WHERE slug = ?", (new_slug,))
    return dict(cursor.fetchone())
