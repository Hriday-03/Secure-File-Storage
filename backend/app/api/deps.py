"""Shared FastAPI dependencies (authorization)."""

import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.jwt_handler import decode_access_token
from app.database.database import get_db
from app.database.models import User
from app.services import auth_service
from app.utils.exceptions import AuthenticationRequiredError

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from the Bearer token.

    Raises AuthenticationRequiredError when missing, invalid, or expired.
    """
    if credentials is None:
        raise AuthenticationRequiredError()

    subject = decode_access_token(credentials.credentials)
    if subject is None:
        raise AuthenticationRequiredError("Invalid or expired token.")

    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise AuthenticationRequiredError("Invalid or expired token.")

    user = auth_service.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise AuthenticationRequiredError()
    return user