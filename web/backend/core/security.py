from cryptography.fernet import Fernet, InvalidToken
import base64
import hashlib


def _derive_fernet_key(raw_key: str) -> bytes:
    """
    Fernet requires exactly 32 bytes encoded as URL-safe base64 (44 chars).
    We derive that from any arbitrary string by SHA-256 hashing it.
    """
    digest = hashlib.sha256(raw_key.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_value(plaintext: str, encryption_key: str) -> str:
    """Encrypt a string. Returns a base64-encoded ciphertext string."""
    if not plaintext:
        return ""
    key = _derive_fernet_key(encryption_key)
    fernet = Fernet(key)
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str, encryption_key: str) -> str:
    """
    Decrypt a string encrypted by encrypt_value.
    Returns empty string if decryption fails (bad key or corrupted data).
    """
    if not ciphertext:
        return ""
    try:
        key = _derive_fernet_key(encryption_key)
        fernet = Fernet(key)
        return fernet.decrypt(ciphertext.encode()).decode()
    except (InvalidToken, Exception):
        return ""


def mask_api_key(api_key: str) -> str:
    """Show only the first 7 and last 4 characters: sk-abc...wxyz"""
    if not api_key or len(api_key) < 12:
        return "****"
    return f"{api_key[:7]}...{api_key[-4:]}"
