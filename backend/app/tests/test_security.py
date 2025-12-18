import pytest
from datetime import datetime, timedelta
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_create_access_token():
    """Test JWT access token creation."""
    data = {"user_id": 1, "role": "candidate"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["user_id"] == 1
    assert decoded["role"] == "candidate"
    assert decoded["type"] == "access"
    assert "exp" in decoded


def test_create_refresh_token():
    """Test JWT refresh token creation."""
    data = {"user_id": 1, "role": "candidate"}
    token = create_refresh_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["user_id"] == 1
    assert decoded["role"] == "candidate"
    assert decoded["type"] == "refresh"
    assert "exp" in decoded


def test_token_expiration():
    """Test token expiration."""
    data = {"user_id": 1, "role": "candidate"}
    
    expired_delta = timedelta(seconds=-1)
    token = create_access_token(data, expires_delta=expired_delta)
    
    decoded = decode_token(token)
    assert decoded is None


def test_invalid_token():
    """Test invalid token decoding."""
    invalid_token = "invalid.token.here"
    decoded = decode_token(invalid_token)
    assert decoded is None
