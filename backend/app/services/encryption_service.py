"""File encryption orchestration combining AES and RSA."""

import base64

from app.crypto import aes, rsa
from app.utils.exceptions import DecryptionError, FileTooLargeError


def encrypt_aes_key(public_key_pem: str, aes_key: bytes) -> str:
    """Encrypt an AES key with the user's RSA public key (base64)."""
    encrypted = rsa.encrypt_rsa(public_key_pem, aes_key)
    return base64.b64encode(encrypted).decode()


def decrypt_aes_key(private_key_pem: str, encrypted_key_b64: str) -> bytes:
    """Recover the AES key encrypted with the user's RSA private key."""
    try:
        encrypted = base64.b64decode(encrypted_key_b64)
    except ValueError as exc:
        raise DecryptionError() from exc
    return rsa.decrypt_rsa(private_key_pem, encrypted)


class _CountingReader:
    """Reader wrapper that counts bytes and enforces a size limit."""

    def __init__(self, reader, max_bytes: int = 0) -> None:
        self.reader = reader
        self.max_bytes = max_bytes
        self.count = 0

    def read(self, size: int) -> bytes:
        data = self.reader.read(size)
        if data and self.max_bytes and self.count + len(data) > self.max_bytes:
            raise FileTooLargeError()
        self.count += len(data)
        return data


def encrypt_file(aes_key: bytes, reader, writer, max_bytes: int = 0) -> int:
    """Stream-encrypt the reader into the writer, returning plaintext size.

    Raises FileTooLargeError if more than max_bytes (0 = unlimited) is read.
    """
    counting = _CountingReader(reader, max_bytes)
    aes.encrypt_stream(aes_key, counting, writer)
    return counting.count


def decrypt_file(aes_key: bytes, reader, writer) -> None:
    """Stream-decrypt the reader into the writer."""
    aes.decrypt_stream(aes_key, reader, writer)
