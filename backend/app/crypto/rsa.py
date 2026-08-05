"""RSA key generation and encryption helpers."""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from app.utils.exceptions import DecryptionError, EncryptionError


def generate_key_pair(key_size: int = 2048) -> tuple[str, str]:
    """Generate an RSA key pair.

    Returns (public_key_pem, private_key_pem).
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return public_pem.decode(), private_pem.decode()


def encrypt_rsa(public_key_pem: str, data: bytes) -> bytes:
    """Encrypt bytes with the given RSA public key (OAEP SHA-256)."""
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        return public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except Exception as exc:
        raise EncryptionError() from exc


def decrypt_rsa(private_key_pem: str, encrypted: bytes) -> bytes:
    """Decrypt bytes with the given RSA private key (OAEP SHA-256)."""
    try:
        private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
        return private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except Exception as exc:
        raise DecryptionError() from exc