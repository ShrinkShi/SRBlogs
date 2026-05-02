from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse

from app.services.audit_service import read_audit_logs, write_audit
from app.services.auth_service import require_admin
from app.services.backup_service import BackupError, backup_path, create_backup, import_backup, list_backups, restore_backup

router = APIRouter(prefix="/admin", tags=["admin-tools"], dependencies=[Depends(require_admin)])


@router.get("/audit/logs")
def audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    action: str = "",
    resource: str = "",
    q: str = "",
):
    return read_audit_logs(limit=limit, offset=offset, action=action, resource=resource, q=q)


@router.post("/backups")
def create_manual_backup(request: Request, actor: str = Depends(require_admin)):
    try:
        item = create_backup()
        write_audit(
            actor=actor,
            action="backup.create",
            resource="backups",
            target=item["name"],
            result="success",
            message="Manual backup created",
            ip=request.client.host if request.client else "",
            detail={"size": item["size"]},
        )
        return item
    except Exception as exc:
        write_audit(actor=actor, action="backup.create", resource="backups", result="failed", message=str(exc))
        raise HTTPException(status_code=500, detail="backup failed") from exc


@router.get("/backups")
def get_backups():
    return list_backups()


@router.get("/backups/{name}/download")
def download_backup(name: str, actor: str = Depends(require_admin)):
    try:
        path = backup_path(name)
        write_audit(actor=actor, action="backup.download", resource="backups", target=name, result="success", message="Backup downloaded")
        return FileResponse(path, media_type="application/zip", filename=path.name)
    except BackupError as exc:
        write_audit(actor=actor, action="backup.download", resource="backups", target=name, result="failed", message=str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="backup not found") from exc


@router.post("/backups/{name}/restore")
def restore_manual_backup(name: str, request: Request, actor: str = Depends(require_admin)):
    try:
        result = restore_backup(name)
        write_audit(
            actor=actor,
            action="backup.restore",
            resource="backups",
            target=name,
            result="success",
            message="Backup restored",
            ip=request.client.host if request.client else "",
            detail=result,
        )
        return result
    except BackupError as exc:
        write_audit(actor=actor, action="backup.restore", resource="backups", target=name, result="failed", message=str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="backup not found") from exc
    except Exception as exc:
        write_audit(actor=actor, action="backup.restore", resource="backups", target=name, result="failed", message=str(exc))
        raise HTTPException(status_code=500, detail="restore failed") from exc


@router.get("/export")
def export_data(actor: str = Depends(require_admin)):
    try:
        item = create_backup(prefix="export-")
        path = backup_path(item["name"])
        write_audit(actor=actor, action="data.export", resource="backups", target=item["name"], result="success", message="Data exported")
        return FileResponse(path, media_type="application/zip", filename=path.name)
    except Exception as exc:
        write_audit(actor=actor, action="data.export", resource="backups", result="failed", message=str(exc))
        raise HTTPException(status_code=500, detail="export failed") from exc


@router.post("/import")
async def import_data(file: UploadFile = File(...), actor: str = Depends(require_admin)):
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=415, detail="Only zip import is supported")
    try:
        result = import_backup(file.file)
        write_audit(actor=actor, action="data.import", resource="backups", target=file.filename, result="success", message="Data imported", detail=result)
        return result
    except BackupError as exc:
        write_audit(actor=actor, action="data.import", resource="backups", target=file.filename, result="failed", message=str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        write_audit(actor=actor, action="data.import", resource="backups", target=file.filename, result="failed", message=str(exc))
        raise HTTPException(status_code=500, detail="import failed") from exc
