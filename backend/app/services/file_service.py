"""File upload and management business logic."""

import os
import re
import uuid
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crypto.aes import generate_aes_key
from app.database.models import File, User
from app.services import encryption_service
from app.services.storage_service import storage
from app.utils.exceptions import (
    EmptyFileError,
    FileTooLargeError,
    FileTypeNotAllowedError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)

ALLOWED_EXTENSIONS = {
    # Documents
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "odt", "ods", "txt", "rtf", "md",
    "csv", "json", "xml", "yaml", "yml", "log",
    # Images
    "jpg", "jpeg", "png", "gif", "webp", "bmp", "tiff", "heic",
    # Video / audio
    "mp4", "mkv", "avi", "mov", "webm", "mp3", "wav", "flac", "ogg", "m4a",
    # Archives
    "zip", "rar", "7z", "tar", "gz", "bz2", "xz",
}

BLOCKED_EXTENSIONS = {
    "exe", "bat", "cmd", "com", "sh", "dll", "msi", "scr", "ps1", "vbs", "js", "jar",
    "class", "pyc", "reg", "app", "pif", "hta", "wsf", "cpl",
}


def sanitize_filename(filename: str) -> str:
    """Sanitize a client-provided filename for safe display and storage."""
    name = Path(filename).name.strip()
    name = re.sub(r"[^\w.\- ]+", "", name)
    name = name.strip(" .")
    if not name:
        raise ValidationError("Invalid filename.")
    if len(name.encode("utf-8")) > 255:
        stem, ext = os.path.splitext(name)
        name = stem[:240] + ext[:10]
    return name


def validate_upload(filename: str, size: int) -> None:
    """Validate extension and size of an upload."""
    extension = Path(filename).suffix.lower().lstrip(".")
    if extension in BLOCKED_EXTENSIONS or extension not in ALLOWED_EXTENSIONS:
        raise FileTypeNotAllowedError()
    if size <= 0:
        raise EmptyFileError()
    if size > settings.max_upload_size_bytes:
        raise FileTooLargeError()


def process_upload(db: Session, user: User, filename: str, mime_type: str | None, reader) -> File:
    """Encrypt an upload to storage and persist its metadata.

    Reader is a binary file-like object positioned at the start of the data.
    """
    original_name = sanitize_filename(filename)
    validate_upload(original_name, 1)
    stored_name = f"{uuid.uuid4().hex}.enc"

    aes_key = generate_aes_key()
    try:
        with storage.open_write(stored_name) as writer:
            size = encryption_service.encrypt_file(
                aes_key, reader, writer, max_bytes=settings.max_upload_size_bytes
            )
    except Exception:
        storage.delete(stored_name)
        raise

    if size <= 0:
        storage.delete(stored_name)
        raise EmptyFileError()

    encrypted_key = encryption_service.encrypt_aes_key(user.public_key, aes_key)
    file_record = File(
        user_id=user.id,
        original_name=original_name,
        stored_name=stored_name,
        encrypted_key=encrypted_key,
        algorithm="AES-256-GCM",
        size=size,
        mime_type=mime_type,
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    return file_record


def get_owned_file(db: Session, user: User, file_id: uuid.UUID) -> File:
    """Return a file owned by the user or raise an error."""
    file_record = db.get(File, file_id)
    if file_record is None:
        raise NotFoundError("File not found.")
    if file_record.user_id != user.id:
        raise ForbiddenError()
    return file_record


def delete_file_record(db: Session, file_record: File) -> None:
    """Delete file metadata and its encrypted blob."""
    db.delete(file_record)
    db.commit()
    storage.delete(file_record.stored_name)


def rename_file_record(db: Session, file_record: File, new_name: str) -> File:
    """Rename a file's display name."""
    sanitized = sanitize_filename(new_name)
    validate_upload(sanitized, file_record.size)
    file_record.original_name = sanitized
    db.commit()
    db.refresh(file_record)
    return file_record


def list_user_files(
    db: Session,
    user: User,
    *,
    search: str | None,
    page: int,
    page_size: int,
    sort_by: str,
    sort_order: str,
) -> tuple[list[File], int]:
    """Return a paginated, sorted list of the user's files and the total count."""
    stmt = select(File).where(File.user_id == user.id)
    count_stmt = select(func.count(File.id)).where(File.user_id == user.id)

    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(File.original_name.ilike(pattern))
        count_stmt = count_stmt.where(File.original_name.ilike(pattern))

    column = {"name": File.original_name, "size": File.size, "date": File.uploaded_at}.get(
        sort_by, File.uploaded_at
    )
    column = column.asc() if sort_order == "asc" else column.desc()
    stmt = stmt.order_by(column)

    total = db.scalar(count_stmt) or 0
    files = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    return list(files), total