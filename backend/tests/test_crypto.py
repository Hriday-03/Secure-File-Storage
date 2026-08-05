"""Unit tests for the cryptography module."""

import io

import pytest

from app.crypto import aes, key_manager, rsa
from app.utils.exceptions import DecryptionError, EncryptionError


class TestAes:
    def test_encrypt_decrypt_roundtrip(self):
        key = aes.generate_aes_key()
        plaintext = b"confidential file contents" * 100
        encrypted = aes.encrypt_data(key, plaintext)
        assert encrypted != plaintext
        assert aes.decrypt_data(key, encrypted) == plaintext

    def test_unique_nonces(self):
        key = aes.generate_aes_key()
        plaintext = b"same data"
        assert aes.encrypt_data(key, plaintext) != aes.encrypt_data(key, plaintext)

    def test_tampered_ciphertext_raises(self):
        key = aes.generate_aes_key()
        encrypted = bytearray(aes.encrypt_data(key, b"attack at dawn"))
        encrypted[-1] ^= 0xFF
        with pytest.raises(DecryptionError):
            aes.decrypt_data(key, bytes(encrypted))

    def test_wrong_key_raises(self):
        key = aes.generate_aes_key()
        other = aes.generate_aes_key()
        encrypted = aes.encrypt_data(key, b"secret")
        with pytest.raises(DecryptionError):
            aes.decrypt_data(other, encrypted)

    def test_key_size(self):
        assert len(aes.generate_aes_key()) == 32

    @pytest.mark.parametrize("size", [1, 100, aes.CHUNK_SIZE - 1, aes.CHUNK_SIZE, aes.CHUNK_SIZE + 1000])
    def test_stream_roundtrip(self, size):
        key = aes.generate_aes_key()
        plaintext = os_random_bytes(size)
        input_stream = io.BytesIO(plaintext)
        output_stream = io.BytesIO()
        aes.encrypt_stream(key, input_stream, output_stream)
        encrypted = output_stream.getvalue()
        assert encrypted != plaintext

        decrypt_out = io.BytesIO()
        aes.decrypt_stream(key, io.BytesIO(encrypted), decrypt_out)
        assert decrypt_out.getvalue() == plaintext

    def test_stream_tampered_raises(self):
        key = aes.generate_aes_key()
        input_stream = io.BytesIO(b"payload" * 1024)
        output_stream = io.BytesIO()
        aes.encrypt_stream(key, input_stream, output_stream)
        corrupted = bytearray(output_stream.getvalue())
        corrupted[len(corrupted) // 2] ^= 0xFF
        with pytest.raises(DecryptionError):
            aes.decrypt_stream(key, io.BytesIO(bytes(corrupted)), io.BytesIO())


class TestRsa:
    def test_keypair_generation(self):
        public_pem, private_pem = rsa.generate_key_pair(2048)
        assert "PUBLIC KEY" in public_pem
        assert "PRIVATE KEY" in private_pem

    def test_encrypt_decrypt_roundtrip(self):
        public_pem, private_pem = rsa.generate_key_pair(2048)
        secret = os_random_bytes(32)  # AES key size
        encrypted = rsa.encrypt_rsa(public_pem, secret)
        assert encrypted != secret
        assert rsa.decrypt_rsa(private_pem, encrypted) == secret

    def test_decrypt_with_wrong_key_raises(self):
        public_pem, _ = rsa.generate_key_pair(2048)
        _, other_private = rsa.generate_key_pair(2048)
        encrypted = rsa.encrypt_rsa(public_pem, b"data")
        with pytest.raises(DecryptionError):
            rsa.decrypt_rsa(other_private, encrypted)


class TestKeyManager:
    def test_private_key_roundtrip(self):
        _, private_pem = rsa.generate_key_pair(2048)
        encrypted = key_manager.encrypt_private_key(private_pem)
        assert encrypted != private_pem
        assert key_manager.decrypt_private_key(encrypted) == private_pem

    def test_tampered_private_key_raises(self):
        _, private_pem = rsa.generate_key_pair(2048)
        encrypted = key_manager.encrypt_private_key(private_pem)
        corrupted = ("A" if encrypted[0] != "A" else "B") + encrypted[1:]
        with pytest.raises(DecryptionError):
            key_manager.decrypt_private_key(corrupted)


def os_random_bytes(size: int) -> bytes:
    import os

    return os.urandom(size)
