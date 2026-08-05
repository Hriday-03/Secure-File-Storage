"""Password hashing and verification utilities."""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against its stored bcrypt hash."""
    return pwd_context.verify(plain_password, password_hash)