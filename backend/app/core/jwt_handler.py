"""JWT access token creation and validation."""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(subject: str) -> str:
    """Create a signed JWT access token for the given subject (user id)."""
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Decode and validate a JWT, returning the subject (user id) or None."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None