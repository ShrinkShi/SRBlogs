from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.services.audit_service import write_audit
from app.services.auth_service import require_admin
from app.services.upload_service import UploadTooLargeError, UploadTypeError, save_upload

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("")
async def upload_image(file: UploadFile = File(...), actor: str = Depends(require_admin)):
    try:
        result = await save_upload(file)
        write_audit(actor=actor, action="upload.create", resource="uploads", target=result.get("filename", file.filename or ""), result="success", message="File uploaded", detail={"size": result.get("size")})
        return result
    except NotImplementedError as exc:
        write_audit(actor=actor, action="upload.create", resource="uploads", target=file.filename or "", result="failed", message=str(exc))
        raise HTTPException(status_code=501, detail=str(exc))
    except UploadTooLargeError as exc:
        write_audit(actor=actor, action="upload.create", resource="uploads", target=file.filename or "", result="failed", message=str(exc))
        raise HTTPException(status_code=413, detail=str(exc))
    except UploadTypeError as exc:
        write_audit(actor=actor, action="upload.create", resource="uploads", target=file.filename or "", result="failed", message=str(exc))
        raise HTTPException(status_code=415, detail=str(exc))
    except ValueError as exc:
        write_audit(actor=actor, action="upload.create", resource="uploads", target=file.filename or "", result="failed", message=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))
