"""
Tests for authentication functionality.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from auth import create_access_token, verify_token, get_password_hash, verify_password
from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 10


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


@patch.dict('os.environ', {'DISABLE_AUTH': 'false'})
def test_protected_endpoint_without_token(client):
    """Test protected endpoint without authentication token."""
    response = client.get("/api/instances")
    assert response.status_code == 401


@patch.dict('os.environ', {'DISABLE_AUTH': 'true'})
def test_protected_endpoint_auth_disabled(client):
    """Test protected endpoint when authentication is disabled."""
    response = client.get("/api/instances")
    # Should not fail due to auth (may fail for other reasons)
    assert response.status_code != 401


def test_verify_token_invalid():
    """Test token verification with invalid token."""
    with pytest.raises(HTTPException):
        verify_token("invalid_token")