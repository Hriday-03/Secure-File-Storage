"""Authentication request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    """User registration payload."""

    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """User login payload."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """JWT token payload returned after login or registration."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class UserOut(BaseModel):
    """Minimal user info returned by /auth/me."""

    id: uuid.UUID
    name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
