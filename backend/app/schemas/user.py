"""User schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    """User representation returned by the API."""

    id: uuid.UUID
    name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdateRequest(BaseModel):
    """Payload for updating profile information."""

    name: str = Field(min_length=2, max_length=255)


class ChangePasswordRequest(BaseModel):
    """Payload for changing the account password."""

    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)