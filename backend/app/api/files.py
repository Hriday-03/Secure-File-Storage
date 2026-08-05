"""File endpoints: upload, list, download, delete, rename."""

import math
import urllib.parse
import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crypto import aes
from app.crypto.key_manager import decrypt_private_key
from app.database.database import get_db
from app.database.models import User
from app.schemas.common import ApiResponse, MessageResponse
from app.schemas.file import FileListResponse, FileResponse, RenameRequest
from app.services import encryption_service, file_service
from app.services.storage_service import storage

router = APIRouter(prefix="/files", tags=["files"])


@router.post(
    "/upload",
    response_model=ApiResponse[FileResponse],
    status_code=201,
    summary="Upload an encrypted file",
)
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[FileResponse]:
    """Validate, encrypt (AES-256-GCM), and store an uploaded file."""
    file_record = file_service.process_upload(
        db,
        current_user,
        file.filename or "",
        file.content_type,
        file.file,
    )
    return ApiResponse(
        success=True,
        message="File uploaded and encrypted successfully.",
        data=file_record,
    )


@router.get("", response_model=ApiResponse[FileListResponse], summary="List files")
def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    sort_by: str = Query("date", pattern="^(name|size|date)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[FileListResponse]:
    """Return a paginated, filtered, sorted list of the user's files."""
    files, total = file_service.list_user_files(
        db,
        current_user,
        search=search,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    data = FileListResponse(
        items=files,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )
    return ApiResponse(success=True, message="Files retrieved.", data=data)


@router.get("/{file_id}", response_model=ApiResponse[FileResponse], summary="Get file")
def get_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[FileResponse]:
    """Return metadata for a single owned file."""
    file_record = file_service.get_owned_file(db, current_user, file_id)
    return ApiResponse(success=True, message="File retrieved.", data=file_record)


@router.get("/{file_id}/download", summary="Download and decrypt a file")
def download_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Stream the decrypted original file to the user."""
    file_record = file_service.get_owned_file(db, current_user, file_id)
    private_key_pem = decrypt_private_key(current_user.encrypted_private_key)
    aes_key = encryption_service.decrypt_aes_key(
        private_key_pem, file_record.encrypted_key
    )

    def iterfile():
        with storage.open_read(file_record.stored_name) as reader:
            yield from aes.decrypt_iter(aes_key, reader)

    encoded_name = urllib.parse.quote(file_record.original_name)
    media_type = file_record.mime_type or "application/octet-stream"
    return StreamingResponse(
        iterfile(),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.delete(
    "/{file_id}",
    response_model=ApiResponse[MessageResponse],
    summary="Delete a file",
)
def delete_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[MessageResponse]:
    """Delete a file's metadata and encrypted blob."""
    file_record = file_service.get_owned_file(db, current_user, file_id)
    file_service.delete_file_record(db, file_record)
    return ApiResponse(
        success=True,
        message="File deleted successfully.",
        data=MessageResponse(message="File deleted successfully."),
    )


@router.put(
    "/{file_id}/rename",
    response_model=ApiResponse[FileResponse],
    summary="Rename a file",
)
def rename_file(
    file_id: uuid.UUID,
    payload: RenameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[FileResponse]:
    """Rename a file's display name."""
    file_record = file_service.get_owned_file(db, current_user, file_id)
    renamed = file_service.rename_file_record(db, file_record, payload.new_name)
    return ApiResponse(success=True, message="File renamed successfully.", data=renamed)