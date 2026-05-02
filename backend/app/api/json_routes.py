from fastapi import APIRouter, Depends
from app.config import get_settings
from app.models.schemas import JsonWrite
from app.services.audit_service import write_audit
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

    @router.put("")
    def write_json(payload: JsonWrite, actor: str = Depends(require_admin)):
        current = store().read()
        action = f"{prefix}.update"
        if isinstance(current, list) and isinstance(payload.data, list):
            if len(payload.data) > len(current):
                action = f"{prefix}.create"
            elif len(payload.data) < len(current):
                action = f"{prefix}.delete"
        try:
            result = store().write(payload.data)
            write_audit(
                actor=actor,
                action=action,
                resource=prefix,
                target=filename,
                result="success",
                message=f"{prefix} data saved",
                detail={"count": len(payload.data) if isinstance(payload.data, list) else None},
            )
            return result
        except Exception as exc:
            write_audit(actor=actor, action=action, resource=prefix, target=filename, result="failed", message=str(exc))
            raise

    return router
