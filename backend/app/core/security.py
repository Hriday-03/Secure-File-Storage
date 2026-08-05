"""Password hashing and verification utilities."""

import bcrypt

_ROUNDS = 12
_BCRYPT_MAX_BYTES = 72


def _encode(password: str) -> bytes:
    """Encode a password as UTF-8, truncated to the bcrypt 72-byte limit."""
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given password."""
    hashed = bcrypt.hashpw(_encode(password), bcrypt.gensalt(rounds=_ROUNDS))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against its stored bcrypt hash."""
    try:
        return bcrypt.checkpw(_encode(plain_password), password_hash.encode("utf-8"))
    except ValueError:
        return False