import os
import io
import zipfile
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlite3 import Connection
from app.db.database import get_db

router = APIRouter()

@router.get("/{slug}")
def download_system(slug: str, db: Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, downloads FROM systems WHERE slug = ? AND is_active = 1", (slug,))
    system = cursor.fetchone()
    
    if not system:
        raise HTTPException(status_code=404, detail="System not found or inactive")
        
    system_dir = os.path.join("system_files", slug)
    
    if not os.path.exists(system_dir) or not os.listdir(system_dir):
        raise HTTPException(
            status_code=404, 
            detail="No files available for this system yet"
        )
        
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(system_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, system_dir)
                zip_file.write(file_path, arcname)
                
    zip_buffer.seek(0)
    
    cursor.execute("UPDATE systems SET downloads = downloads + 1 WHERE id = ?", (system["id"],))
    db.commit()
    
    headers = {
        "Content-Disposition": f'attachment; filename="{slug}.zip"'
    }
    
    return StreamingResponse(
        zip_buffer, 
        media_type="application/zip", 
        headers=headers
    )
