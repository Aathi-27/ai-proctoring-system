import pytest
from fastapi import status


def test_list_users_as_admin(client, admin_headers, test_user):
    """Test that admin can list all users."""
    response = client.get("/api/v1/users/", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_list_users_as_candidate_fails(client, auth_headers):
    """Test that candidate cannot list all users."""
    response = client.get("/api/v1/users/", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_own_user(client, auth_headers, test_user):
    """Test that user can get their own information."""
    response = client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email


def test_get_other_user_as_candidate_fails(client, auth_headers, test_admin):
    """Test that candidate cannot view other users."""
    response = client.get(f"/api/v1/users/{test_admin.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_other_user_as_admin(client, admin_headers, test_user):
    """Test that admin can view other users."""
    response = client.get(f"/api/v1/users/{test_user.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email


def test_create_user_as_admin(client, admin_headers):
    """Test that admin can create new users with any role."""
    response = client.post(
        "/api/v1/users/",
        headers=admin_headers,
        json={
            "email": "newinvigilator@example.com",
            "password": "InvigilatorPass123!",
            "full_name": "New Invigilator",
            "role": "invigilator"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newinvigilator@example.com"
    assert data["role"] == "invigilator"


def test_create_user_as_candidate_fails(client, auth_headers):
    """Test that candidate cannot create users."""
    response = client.post(
        "/api/v1/users/",
        headers=auth_headers,
        json={
            "email": "unauthorized@example.com",
            "password": "Password123!",
            "full_name": "Unauthorized User",
            "role": "candidate"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_user_as_admin(client, admin_headers, test_user):
    """Test that admin can delete users."""
    response = client.delete(f"/api/v1/users/{test_user.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    get_response = client.get(f"/api/v1/users/{test_user.id}", headers=admin_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_as_candidate_fails(client, auth_headers, test_admin):
    """Test that candidate cannot delete users."""
    response = client.delete(f"/api/v1/users/{test_admin.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_cannot_delete_self(client, admin_headers, test_admin):
    """Test that admin cannot delete themselves."""
    response = client.delete(f"/api/v1/users/{test_admin.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
