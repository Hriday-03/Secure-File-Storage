"""Authentication endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.database import get_db
from app.database.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.schemas.common import ApiResponse, MessageResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=ApiResponse[TokenResponse],
    status_code=201,
    summary="Register a new account",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> ApiResponse[TokenResponse]:
    """Create an account and return an access token."""
    user = auth_service.register_user(db, payload.name, payload.email, payload.password)
    data = auth_service.build_token_payload(user)
    return ApiResponse(success=True, message="Account created successfully.", data=data)


@router.post("/login", response_model=ApiResponse[TokenResponse], summary="Log in")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> ApiResponse[TokenResponse]:
    """Authenticate credentials and return an access token."""
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    data = auth_service.build_token_payload(user)
    return ApiResponse(success=True, message="Logged in successfully.", data=data)


@router.post("/logout", response_model=ApiResponse[MessageResponse], summary="Log out")
def logout(current_user: User = Depends(get_current_user)) -> ApiResponse[MessageResponse]:
    """Invalidate the client session (client discards the token)."""
    return ApiResponse(
        success=True,
        message="Logged out successfully.",
        data=MessageResponse(message="Logged out successfully."),
    )


@router.get("/me", response_model=ApiResponse[UserOut], summary="Get current user")
def me(current_user: User = Depends(get_current_user)) -> ApiResponse[UserOut]:
    """Return the authenticated user's profile."""
    return ApiResponse(success=True, message="User profile.", data=current_user)