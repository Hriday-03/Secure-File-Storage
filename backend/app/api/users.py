"""User endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import hash_password, verify_password
from app.database.database import get_db
from app.database.models import User
from app.schemas.common import ApiResponse
from app.schemas.user import ChangePasswordRequest, ProfileUpdateRequest, UserResponse
from app.utils.exceptions import InvalidCredentialsError, ValidationError

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=ApiResponse[UserResponse], summary="Get profile")
def get_profile(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserResponse]:
    """Return the authenticated user's profile."""
    return ApiResponse(success=True, message="Profile retrieved.", data=current_user)


@router.put("/profile", response_model=ApiResponse[UserResponse], summary="Update profile")
def update_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserResponse]:
    """Update the authenticated user's display name."""
    current_user.name = payload.name.strip()
    db.commit()
    db.refresh(current_user)
    return ApiResponse(success=True, message="Profile updated.", data=current_user)


@router.post("/change-password", response_model=ApiResponse[dict], summary="Change password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[dict]:
    """Verify the current password and set a new one."""
    if not verify_password(payload.current_password, current_user.password_hash):
        raise InvalidCredentialsError("Current password is incorrect.")

    if payload.current_password == payload.new_password:
        raise ValidationError("New password must be different from the current password.")

    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    return ApiResponse(success=True, message="Password changed.", data={})