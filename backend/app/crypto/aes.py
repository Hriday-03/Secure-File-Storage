"""AES-256-GCM authenticated encryption helpers."""

import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.utils.exceptions import DecryptionError, EncryptionError

KEY_SIZE = 32
NONCE_SIZE = 12


def generate_aes_key() -> bytes:
    """Generate a cryptographically secure random 256-bit AES key."""
    return os.urandom(KEY_SIZE)


def encrypt_data(key: bytes, plaintext: bytes) -> bytes:
    """Encrypt data with AES-256-GCM.

    Returns nonce || ciphertext || tag.
    """
    try:
        nonce = os.urandom(NONCE_SIZE)
        ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
        return nonce + ciphertext
    except Exception as exc:  # pragma: no cover - defensive
        raise EncryptionError() from exc


def decrypt_data(key: bytes, encrypted: bytes) -> bytes:
    """Decrypt data produced by encrypt_data.

    Raises DecryptionError on invalid key or tampered data.
    """
    if len(encrypted) < NONCE_SIZE:
        raise DecryptionError()
    nonce, ciphertext = encrypted[:NONCE_SIZE], encrypted[NONCE_SIZE:]
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, None)
    except (InvalidTag, ValueError) as exc:
        raise DecryptionError() from exc