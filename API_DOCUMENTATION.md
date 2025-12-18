# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication Endpoints

#### POST /auth/register

Register a new user (Candidate or Admin only).

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "candidate"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "candidate",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Allowed Roles for Self-Registration:**
- `candidate`
- `admin`

**Errors:**
- `400`: Email already registered or invalid role
- `422`: Validation error (invalid email, password too short, etc.)

---

#### POST /auth/login

Login and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token Details:**
- **Access Token**: Expires in 15 minutes
- **Refresh Token**: Expires in 7 days
- **Token Type**: bearer

**Errors:**
- `401`: Incorrect email or password
- `403`: Inactive user
- `422`: Validation error

---

#### POST /auth/refresh

Exchange a refresh token for new tokens.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Notes:**
- Old refresh token is automatically revoked
- New refresh token must be used for subsequent refresh requests

**Errors:**
- `401`: Invalid, revoked, or expired refresh token
- `422`: Validation error

---

#### POST /auth/logout

Logout and revoke refresh token.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (204 No Content):**
```
(empty response)
```

**Errors:**
- `401`: Invalid or missing access token
- `422`: Validation error

---

#### GET /auth/me

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "candidate",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Errors:**
- `401`: Invalid or missing access token
- `403`: Inactive user
- `404`: User not found

---

### User Management Endpoints

#### GET /users/

List all users (Admin and System Integrator only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "email": "user1@example.com",
    "full_name": "User One",
    "role": "candidate",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z"
  },
  {
    "id": 2,
    "email": "user2@example.com",
    "full_name": "User Two",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-02T12:00:00Z"
  }
]
```

**Required Roles:**
- `admin`
- `system_integrator`

**Errors:**
- `401`: Invalid or missing access token
- `403`: Insufficient permissions

---

#### GET /users/{user_id}

Get user by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "candidate",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Access Control:**
- Users can view their own profile
- Admins and System Integrators can view any profile

**Errors:**
- `401`: Invalid or missing access token
- `403`: Not authorized to view this user
- `404`: User not found

---

#### POST /users/

Create a new user (Admin and System Integrator only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "full_name": "New User",
  "role": "invigilator"
}
```

**Available Roles:**
- `candidate`
- `invigilator`
- `admin`
- `system_integrator`

**Response (201 Created):**
```json
{
  "id": 3,
  "email": "newuser@example.com",
  "full_name": "New User",
  "role": "invigilator",
  "is_active": true,
  "created_at": "2024-01-03T12:00:00Z"
}
```

**Required Roles:**
- `admin`
- `system_integrator`

**Errors:**
- `400`: Email already registered
- `401`: Invalid or missing access token
- `403`: Insufficient permissions
- `422`: Validation error

---

#### DELETE /users/{user_id}

Delete a user (Admin and System Integrator only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content):**
```
(empty response)
```

**Notes:**
- Cannot delete yourself
- Deleting a user will cascade delete their refresh tokens

**Required Roles:**
- `admin`
- `system_integrator`

**Errors:**
- `400`: Cannot delete yourself
- `401`: Invalid or missing access token
- `403`: Insufficient permissions
- `404`: User not found

---

## User Roles

### Candidate
- Can register via `/auth/register`
- Can take exams (Phase 2)
- Can view own evidence (Phase 2)
- Can view own profile

### Invigilator
- Created by admins via `/users/`
- Can monitor assigned exams (Phase 2)
- Can view candidate evidence for assigned exams (Phase 2)

### Admin
- Can register via `/auth/register` or be created by other admins
- Full access to user management
- Can create/delete users
- Can view all user profiles
- System configuration access

### System Integrator
- Created by admins via `/users/`
- API access for integrations
- User management access
- Cannot self-register

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `204 No Content`: Request succeeded with no response body
- `400 Bad Request`: Invalid request (e.g., duplicate email, business logic violation)
- `401 Unauthorized`: Authentication failed or token invalid/expired
- `403 Forbidden`: Insufficient permissions or inactive user
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error (e.g., invalid email format, password too short)

---

## JWT Token Structure

### Access Token Claims

```json
{
  "user_id": 1,
  "role": "candidate",
  "exp": 1609459200,
  "type": "access"
}
```

### Refresh Token Claims

```json
{
  "user_id": 1,
  "role": "candidate",
  "exp": 1610064000,
  "type": "refresh"
}
```

**Note:** Tokens can also include `exam_id` claim for exam-scoped access (Phase 2 feature).

---

## Rate Limiting

Currently, no rate limiting is implemented. This will be added in a future release.

---

## CORS Configuration

The API allows requests from:
- `http://localhost:3000` (Frontend development server)

Configure additional origins in the `.env` file:

```env
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
```

---

## Interactive API Documentation

Once the backend is running, you can access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints and their parameters
- Try out endpoints directly from the browser
- See request/response schemas
- Authenticate and test protected endpoints
