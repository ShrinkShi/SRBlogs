from fastapi import APIRouter, Depends
from app.config import get_settings
from app.models.schemas import JsonWrite
from app.services.auth_service import require_admin
from app.services.json_service import JsonStore

DEFAULTS = {
    "friends.json": [],
    "projects.json": [],
    "music.json": [],
    "photos/photos.json": [],
    "settings.json": {},
}


def make_json_router(prefix: str, filename: str, tag: str) -> APIRouter:
    router = APIRouter(prefix=f"/{prefix}", tags=[tag])

    def store() -> JsonStore:
        return JsonStore(get_settings().data_path, filename, DEFAULTS.get(filename, []))

    @router.get("")
    def read_json():
        return store().read()

    @router.put("", dependencies=[Depends(require_admin)])
    def write_json(payload: JsonWrite):
        return store().write(payload.data)

    return router
