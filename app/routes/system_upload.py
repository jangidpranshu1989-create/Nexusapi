"""
Allows a system's owner (or admin) to upload a ZIP file containing their
project's code. The ZIP is extracted into system_files/{slug}/, replacing
any existing files for that system.
"""

import os
import shutil
import zipfile
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlite3 import Connection
from app.db.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()

MAX_UPLOAD_SIZE_MB = 20


@router.post("/{slug}/upload-files")
async def upload_system_files(
    slug: str,
    file: UploadFile = File(...),
    db: Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM systems WHERE slug = ?", (slug,))
    system = cursor.fetchone()

    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    if current_user["role"] != "admin" and system["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="You can only upload files for your own systems")

    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are accepted")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_UPLOAD_SIZE_MB}MB")

    try:
        zip_buffer = io.BytesIO(contents)
        with zipfile.ZipFile(zip_buffer) as zf:
            bad_file = zf.testzip()
            if bad_file:
                raise HTTPException(status_code=400, detail=f"Corrupt file in zip: {bad_file}")

            target_dir = os.path.join("system_files", slug)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            os.makedirs(target_dir, exist_ok=True)

            for member in zf.namelist():
                if member.startswith("/") or ".." in member:
                    continue
                zf.extract(member, target_dir)

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip file")

    return {"message": "Files uploaded successfully", "slug": slug}
