from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import get_settings
from app.api.auth import router as auth_router
from app.api.content_routes import make_content_router
from app.api.json_routes import make_json_router
from app.api.about import router as about_router
from app.api.comments import router as comments_router
from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.api.dashboard import router as dashboard_router

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings.data_path.mkdir(parents=True, exist_ok=True)
(settings.data_path / "uploads").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.data_path / "uploads"), name="uploads")

app.include_router(auth_router, prefix="/api")
app.include_router(make_content_router("posts", "posts"), prefix="/api")
app.include_router(make_content_router("moments", "moments"), prefix="/api")
app.include_router(make_content_router("chatters", "chatters"), prefix="/api")
app.include_router(about_router, prefix="/api")
app.include_router(make_json_router("friends", "friends.json", "friends"), prefix="/api")
app.include_router(make_json_router("projects", "projects.json", "projects"), prefix="/api")
app.include_router(make_json_router("music", "music.json", "music"), prefix="/api")
app.include_router(make_json_router("photos", "photos/photos.json", "photos"), prefix="/api")
app.include_router(make_json_router("settings", "settings.json", "settings"), prefix="/api")
app.include_router(comments_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"ok": True, "app": settings.app_name}
