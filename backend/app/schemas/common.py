"""Shared API schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Consistent API response envelope."""

    success: bool = True
    message: str = ""
    data: T | None = None
    error: str | None = None


class MessageResponse(BaseModel):
    """Simple message payload."""

    message: str