"""User endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.database import get_db
from app.database.models import File, User
from app.schemas.common import ApiResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=ApiResponse[UserResponse], summary="Get profile")
def get_profile(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserResponse]:
    """Return the authenticated user's profile."""
    return ApiResponse(success=True, message="Profile retrieved.", data=current_user)