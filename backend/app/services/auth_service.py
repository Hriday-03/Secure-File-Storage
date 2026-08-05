"""Authentication business logic."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.jwt_handler import create_access_token
from app.core.security import hash_password, verify_password
from app.crypto.key_manager import encrypt_private_key
from app.crypto.rsa import generate_key_pair
from app.database.models import User
from app.utils.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    NotFoundError,
)


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    """Return a user by id, or None."""
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    """Return a user by normalized email, or None."""
    return db.scalar(select(User).where(User.email == email.lower().strip()))


def register_user(db: Session, name: str, email: str, password: str) -> User:
    """Create a new user with a fresh RSA key pair.

    Raises EmailAlreadyRegisteredError if the email is taken.
    """
    normalized_email = email.lower().strip()
    if get_user_by_email(db, normalized_email) is not None:
        raise EmailAlreadyRegisteredError()

    public_pem, private_pem = generate_key_pair(settings.RSA_KEY_SIZE)
    user = User(
        name=name.strip(),
        email=normalized_email,
        password_hash=hash_password(password),
        public_key=public_pem,
        encrypted_private_key=encrypt_private_key(private_pem),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Validate credentials and return the user.

    Raises InvalidCredentialsError on failure.
    """
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()
    if not user.is_active:
        raise InvalidCredentialsError()
    return user


def build_token_payload(user: User) -> dict:
    """Build the access token response payload for a user."""
    return {
        "access_token": create_access_token(str(user.id)),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user,
    }


def require_user(db: Session, user_id: uuid.UUID) -> User:
    """Return the user or raise NotFoundError."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise NotFoundError("User not found.")
    return user