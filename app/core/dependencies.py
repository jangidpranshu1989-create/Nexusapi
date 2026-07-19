from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlite3 import Connection
from app.db.database import get_db
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Connection = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception
        
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (int(user_id),))
    user = cursor.fetchone()
    
    if user is None:
        raise credentials_exception
        
    return dict(user)

def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def require_developer_or_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ("developer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Developer or admin access required"
        )
    return current_user
