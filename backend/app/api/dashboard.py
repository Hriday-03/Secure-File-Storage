"""Dashboard endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.database import get_db
from app.database.models import File, User
from app.schemas.common import ApiResponse
from pydantic import BaseModel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    """Aggregated storage statistics for a user."""

    total_files: int
    total_size: int
    last_upload_at: datetime | None
    algorithm: str


@router.get("/stats", response_model=ApiResponse[DashboardStats], summary="Get dashboard stats")
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[DashboardStats]:
    """Return storage statistics for the authenticated user."""
    total_files = db.scalar(
        select(func.count(File.id)).where(File.user_id == current_user.id)
    ) or 0
    total_size = db.scalar(
        select(func.coalesce(func.sum(File.size), 0)).where(File.user_id == current_user.id)
    ) or 0
    last_upload_at = db.scalar(
        select(func.max(File.uploaded_at)).where(File.user_id == current_user.id)
    )

    stats = DashboardStats(
        total_files=total_files,
        total_size=total_size,
        last_upload_at=last_upload_at,
        algorithm="AES-256-GCM",
    )
    return ApiResponse(success=True, message="Dashboard statistics.", data=stats)