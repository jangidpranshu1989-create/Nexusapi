from fastapi import APIRouter, Depends, HTTPException, status
from sqlite3 import Connection
from typing import List
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.reviews import ReviewCreate, ReviewResponse

router = APIRouter()

@router.get("/{slug}/reviews", response_model=List[ReviewResponse])
def get_system_reviews(slug: str, db: Connection = Depends(get_db)):
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM systems WHERE slug = ?", (slug,))
    system = cursor.fetchone()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
        
    system_id = system["id"]
    
    query = """
        SELECT r.id, r.system_id, r.user_id, u.name as user_name, 
               r.rating, r.comment, r.created_at
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.system_id = ?
        ORDER BY r.created_at DESC
    """
    cursor.execute(query, (system_id,))
    reviews = cursor.fetchall()
    
    return [dict(row) for row in reviews]

@router.post("/{slug}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_system_review(
    slug: str,
    review: ReviewCreate,
    db: Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM systems WHERE slug = ?", (slug,))
    system = cursor.fetchone()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
        
    system_id = system["id"]
    user_id = current_user["id"]
    
    cursor.execute("SELECT id FROM reviews WHERE system_id = ? AND user_id = ?", (system_id, user_id))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="You have already reviewed this system")
        
    cursor.execute(
        "INSERT INTO reviews (system_id, user_id, rating, comment) VALUES (?, ?, ?, ?)",
        (system_id, user_id, review.rating, review.comment)
    )
    db.commit()
    review_id = cursor.lastrowid
    
    cursor.execute("SELECT AVG(rating) as avg_rating FROM reviews WHERE system_id = ?", (system_id,))
    avg_result = cursor.fetchone()
    avg_rating = round(avg_result["avg_rating"], 1) if avg_result["avg_rating"] is not None else 0.0
    
    cursor.execute("UPDATE systems SET rating = ? WHERE id = ?", (avg_rating, system_id))
    db.commit()
    
    fetch_query = """
        SELECT r.id, r.system_id, r.user_id, u.name as user_name, 
               r.rating, r.comment, r.created_at
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.id = ?
    """
    cursor.execute(fetch_query, (review_id,))
    new_review = cursor.fetchone()
    
    return dict(new_review)
