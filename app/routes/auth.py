from fastapi import APIRouter, Depends, HTTPException, status
from sqlite3 import Connection
from app.db.database import get_db
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Connection = Depends(get_db)):
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user.password)
    
    cursor.execute(
        "INSERT INTO users (email, password_hash, name, role) VALUES (?, ?, ?, ?)",
        (user.email, hashed_pw, user.name, "user")
    )
    db.commit()
    user_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    new_user = cursor.fetchone()
    
    return dict(new_user)

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = {"sub": str(db_user["id"]), "role": db_user["role"]}
    token = create_access_token(data=token_data)
    
    return {"access_token": token, "token_type": "bearer", "role": db_user["role"]}
