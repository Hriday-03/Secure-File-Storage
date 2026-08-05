"""Master key derivation and encrypted key storage helpers."""

import base64
from functools import lru_cache

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from app.core.config import settings
from app.crypto.aes import decrypt_data, encrypt_data

_SALT = b"secure-file-storage-master-salt-v1"
_INFO = b"aes-256-gcm-master-key"


@lru_cache
def _master_key() -> bytes:
    """Derive the server master key from SECRET_KEY using HKDF-SHA256."""
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=_SALT, info=_INFO)
    return hkdf.derive(settings.SECRET_KEY.encode())


def encrypt_private_key(private_key_pem: str) -> str:
    """Encrypt an RSA private key with the master key, returning base64."""
    encrypted = encrypt_data(_master_key(), private_key_pem.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_private_key(encrypted_b64: str) -> str:
    """Decrypt an RSA private key encrypted with the master key."""
    encrypted = base64.b64decode(encrypted_b64.encode())
    return decrypt_data(_master_key(), encrypted).decode()