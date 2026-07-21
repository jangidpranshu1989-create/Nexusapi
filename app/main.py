import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from app.routes import auth, systems, reviews, categories, download, developer, system_upload, admin, profile, settings

load_dotenv()

app = FastAPI(title="NexusAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(systems.router, prefix="/api/v1/systems", tags=["Systems"])
app.include_router(reviews.router, prefix="/api/v1/systems", tags=["Reviews"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(download.router, prefix="/api/v1/download", tags=["Download"])
app.include_router(developer.router, prefix="/api/v1/developer", tags=["Developer"])
app.include_router(system_upload.router, prefix="/api/v1/systems", tags=["System Upload"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["Profile"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["Settings"])

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

@app.get("/login")
def serve_login():
    return FileResponse("frontend/login.html")

@app.get("/register")
def serve_register():
    return FileResponse("frontend/register.html")

@app.get("/developer-verify")
def serve_developer_verify():
    return FileResponse("frontend/developer-verify.html")

@app.get("/dashboard")
def serve_dashboard():
    return FileResponse("frontend/dashboard.html")

@app.get("/settings")
def serve_settings():
    return FileResponse("frontend/settings.html")

@app.get("/profile")
def serve_profile():
    return FileResponse("frontend/profile.html")

@app.get("/admin")
def serve_admin():
    return FileResponse("frontend/admin.html")

@app.get("/manifest.json")
def serve_manifest():
    return FileResponse("frontend/manifest.json")

@app.get("/sw.js")
def serve_sw():
    return FileResponse("frontend/sw.js")

@app.get("/systems/{slug}")
def serve_system_detail(slug: str):
    return FileResponse("frontend/system-detail.html")
