from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import get_settings
from app.api.auth import router as auth_router
from app.api.content_routes import make_content_router
from app.api.json_routes import make_json_router
from app.api.about import about_page_router, contact_router
from app.api.about import router as about_router
from app.api.comments import admin_router as comments_admin_router
from app.api.comments import router as comments_router
from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.api.dashboard import router as dashboard_router
from app.api.settings import router as settings_router
from app.api.pages import router as pages_router
from app.api.discovery import router as discovery_router
from app.api.seo import router as seo_router
from app.api.admin_tools import router as admin_tools_router
from app.api.updates import router as updates_router
from app.api.install import router as install_router
from app.services.install_service import ensure_base_data_dirs, is_installed

settings = get_settings()
app = FastAPI(title=settings.app_name)

NO_STORE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}


def _error_code(status_code: int) -> str:
    return {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        413: "PAYLOAD_TOO_LARGE",
        415: "UNSUPPORTED_MEDIA_TYPE",
        503: "SERVICE_UNAVAILABLE",
        500: "INTERNAL_SERVER_ERROR",
    }.get(status_code, "ERROR")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    detail = exc.detail
    message = detail if isinstance(detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": _error_code(exc.status_code), "message": message, "detail": detail if not isinstance(detail, str) else {}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"code": "BAD_REQUEST", "message": "Validation failed", "detail": jsonable_encoder(exc.errors())},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensure_base_data_dirs()
app.mount("/uploads", StaticFiles(directory=settings.data_path / "uploads"), name="uploads")


@app.middleware("http")
async def install_guard(request: Request, call_next):
    path = request.url.path
    if request.method == "OPTIONS":
        return await call_next(request)
    allowed = {
        "/api/health",
        "/api/install/status",
        "/api/install",
    }
    if path.startswith("/api/") and path not in allowed and not is_installed():
        return JSONResponse(
            status_code=503,
            content={"code": "INSTALL_REQUIRED", "message": "SRBlogs 尚未完成安装。", "detail": {"installUrl": "/install"}},
        )
    return await call_next(request)


@app.middleware("http")
async def api_no_store(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers.update(NO_STORE_HEADERS)
    return response

app.include_router(install_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(make_content_router("posts", "posts"), prefix="/api")
app.include_router(make_content_router("moments", "moments"), prefix="/api")
app.include_router(make_content_router("chatters", "chatters"), prefix="/api")
app.include_router(about_router, prefix="/api")
app.include_router(about_page_router, prefix="/api")
app.include_router(contact_router, prefix="/api")
app.include_router(make_json_router("friends", "friends.json", "friends"), prefix="/api")
app.include_router(make_json_router("projects", "projects.json", "projects"), prefix="/api")
app.include_router(make_json_router("music", "music.json", "music"), prefix="/api")
app.include_router(make_json_router("photos", "photos/photos.json", "photos"), prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(pages_router, prefix="/api")
app.include_router(comments_router, prefix="/api")
app.include_router(comments_admin_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(discovery_router, prefix="/api")
app.include_router(admin_tools_router, prefix="/api")
app.include_router(updates_router, prefix="/api")
app.include_router(seo_router)


@app.get("/api/health")
def health():
    return {"ok": True, "app": settings.app_name}
