from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.services.auth_service import require_admin
from app.services.upload_service import UploadTooLargeError, UploadTypeError, save_upload

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", dependencies=[Depends(require_admin)])
async def upload_image(file: UploadFile = File(...)):
    try:
        return await save_upload(file)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc))
    except UploadTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc))
    except UploadTypeError as exc:
        raise HTTPException(status_code=415, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
