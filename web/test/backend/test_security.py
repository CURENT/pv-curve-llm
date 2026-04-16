"""Tests for the security (encryption) utilities."""
from web.backend.core.security import encrypt_value, decrypt_value, mask_api_key


def test_encrypt_decrypt_roundtrip():
    plaintext = "sk-supersecretapikey1234"
    key = "my-secret-encryption-key"
    encrypted = encrypt_value(plaintext, key)
    assert encrypted != plaintext
    assert decrypt_value(encrypted, key) == plaintext


def test_wrong_key_returns_empty():
    encrypted = encrypt_value("secret", "key-A")
    result = decrypt_value(encrypted, "key-B")
    assert result == ""


def test_empty_value():
    assert encrypt_value("", "key") == ""
    assert decrypt_value("", "key") == ""


def test_mask_api_key_normal():
    masked = mask_api_key("sk-abcdefghijklmnop")
    assert masked.startswith("sk-abcd")
    assert masked.endswith("lmno") or "..." in masked


def test_mask_api_key_short():
    assert mask_api_key("short") == "****"


def test_mask_api_key_empty():
    assert mask_api_key("") == "****"
