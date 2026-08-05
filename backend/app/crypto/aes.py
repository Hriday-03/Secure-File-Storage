"""AES-256-GCM authenticated encryption helpers."""

import os
import struct

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.utils.exceptions import DecryptionError, EncryptionError

KEY_SIZE = 32
NONCE_SIZE = 12
TAG_SIZE = 16
CHUNK_SIZE = 1024 * 1024  # 1 MiB streaming chunk size
_LEN_HEADER = 4


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


def encrypt_stream(key: bytes, reader, writer) -> None:
    """Encrypt a stream chunk by chunk.

    On-disk format per chunk: [4-byte LE ciphertext length][12-byte nonce][ciphertext + tag].
    """
    while True:
        chunk = reader.read(CHUNK_SIZE)
        if not chunk:
            break
        nonce = os.urandom(NONCE_SIZE)
        try:
            ciphertext = AESGCM(key).encrypt(nonce, chunk, None)
        except Exception as exc:  # pragma: no cover - defensive
            raise EncryptionError() from exc
        writer.write(struct.pack("<I", len(ciphertext)) + nonce + ciphertext)


def decrypt_iter(key: bytes, reader):
    """Yield decrypted plaintext chunks from an encrypt_stream file.

    Raises DecryptionError on invalid key or tampered data.
    """
    while True:
        header = reader.read(_LEN_HEADER + NONCE_SIZE)
        if not header:
            return
        if len(header) < _LEN_HEADER + NONCE_SIZE:
            raise DecryptionError()
        ciphertext_len, nonce = struct.unpack("<I", header[:_LEN_HEADER])[0], header[_LEN_HEADER:]
        ciphertext = reader.read(ciphertext_len)
        if len(ciphertext) != ciphertext_len:
            raise DecryptionError()
        try:
            yield AESGCM(key).decrypt(nonce, ciphertext, None)
        except (InvalidTag, ValueError) as exc:
            raise DecryptionError() from exc


def decrypt_stream(key: bytes, reader, writer) -> None:
    """Decrypt a stream produced by encrypt_stream.

    Raises DecryptionError on invalid key or tampered data.
    """
    for plaintext in decrypt_iter(key, reader):
        writer.write(plaintext)