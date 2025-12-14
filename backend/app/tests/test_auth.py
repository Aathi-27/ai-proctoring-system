import pytest
from fastapi import status


def test_register_candidate(client):
    """Test candidate registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newcandidate@example.com",
            "password": "NewPass123!",
            "full_name": "New Candidate",
            "role": "candidate"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newcandidate@example.com"
    assert data["full_name"] == "New Candidate"
    assert data["role"] == "candidate"
    assert data["is_active"] is True
    assert "id" in data


def test_register_admin(client):
    """Test admin registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newadmin@example.com",
            "password": "AdminPass123!",
            "full_name": "New Admin",
            "role": "admin"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["role"] == "admin"


def test_register_invigilator_fails(client):
    """Test that invigilator cannot register directly."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newinvigilator@example.com",
            "password": "InvigilatorPass123!",
            "full_name": "New Invigilator",
            "role": "invigilator"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email fails."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "AnotherPass123!",
            "full_name": "Another User",
            "role": "candidate"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123!"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token(client, test_user):
    """Test refresh token exchange."""
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123!"
        }
    )
    refresh_token = login_response.json()["refresh_token"]
    
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_token


def test_refresh_token_reuse_fails(client, test_user):
    """Test that refresh token cannot be reused."""
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123!"
        }
    )
    refresh_token = login_response.json()["refresh_token"]
    
    client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers):
    """Test getting current user information."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "candidate"


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_logout(client, test_user, auth_headers):
    """Test logout functionality."""
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123!"
        }
    )
    refresh_token = login_response.json()["refresh_token"]
    
    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
