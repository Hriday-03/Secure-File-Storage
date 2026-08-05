"""File schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileResponse(BaseModel):
    """File metadata returned by the API."""

    id: uuid.UUID
    original_name: str
    size: int
    mime_type: str | None
    algorithm: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileListResponse(BaseModel):
    """Paginated file list."""

    items: list[FileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RenameRequest(BaseModel):
    """Rename payload."""

    new_name: str
