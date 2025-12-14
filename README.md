# Exam Proctoring System - Authentication & User Management

A comprehensive JWT-based authentication system with role-based access control (RBAC) for an online exam proctoring platform.

## Features

### Authentication
- ✅ JWT-based authentication (Access + Refresh tokens)
- ✅ Secure password hashing with bcrypt
- ✅ Token expiration (Access: 15 min, Refresh: 7 days)
- ✅ Automatic token refresh
- ✅ Token invalidation on logout

### User Roles
- **Candidate**: Can take exams, view their own evidence
- **Invigilator**: Can monitor assigned exams
- **Admin**: Full system access, user management
- **System Integrator**: API access, system integrations

### RBAC (Role-Based Access Control)
- Route protection by role
- Exam-scoped access control
- Evidence access restrictions
- Self-service profile viewing

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user (Candidate/Admin only)
- `POST /api/v1/auth/login` - Login and receive tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout and revoke tokens
- `GET /api/v1/auth/me` - Get current user info

#### User Management
- `GET /api/v1/users/` - List all users (Admin/System Integrator only)
- `GET /api/v1/users/{id}` - Get user by ID
- `POST /api/v1/users/` - Create user (Admin/System Integrator only)
- `DELETE /api/v1/users/{id}` - Delete user (Admin/System Integrator only)

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **PyJWT** - JWT token handling
- **Passlib** - Password hashing (bcrypt)
- **Pydantic** - Data validation

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Axios** - HTTP client with interceptors
- **js-cookie** - Cookie management
- **Tailwind CSS** - Utility-first CSS

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL (via Docker)

### Backend Setup

1. **Start PostgreSQL**
   ```bash
   docker-compose up -d
   ```

2. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY to a secure random string (min 32 chars)
   ```

5. **Run the application**
   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env.local
   # Edit if needed (default: http://localhost:8000/api/v1)
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000

## Testing

### Run Backend Tests
```bash
cd backend
pytest
```

### Test Coverage
```bash
pytest --cov=app --cov-report=html
```

Coverage reports will be generated in `htmlcov/index.html`.

## API Usage Examples

### Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "candidate@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe",
    "role": "candidate"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "candidate@example.com",
    "password": "SecurePass123!"
  }'
```

### Access Protected Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

## Security Features

1. **Password Security**
   - Bcrypt hashing with salt
   - Minimum 8 characters required
   - Never stored in plaintext

2. **Token Security**
   - Short-lived access tokens (15 minutes)
   - Longer refresh tokens (7 days)
   - Tokens include: user_id, role, expiration
   - Refresh tokens stored in database
   - Token revocation on logout

3. **API Security**
   - CORS configured for frontend origin
   - Bearer token authentication
   - Role-based authorization
   - Automatic token refresh with interceptors

4. **Environment Variables**
   - Secrets stored in .env files
   - .env files excluded from version control
   - Example files provided for reference

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### Refresh Tokens Table
```sql
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   └── users.py
│   │   │   └── api.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── middleware/
│   │   │   └── auth.py
│   │   ├── tests/
│   │   │   ├── conftest.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_rbac.py
│   │   │   └── test_security.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── unauthorized/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   └── lib/
│   │       ├── api.ts
│   │       └── auth.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Test Coverage

The test suite includes:
- ✅ Unit tests for JWT generation/validation
- ✅ Integration tests for all auth endpoints
- ✅ RBAC authorization tests
- ✅ Password hashing tests
- ✅ Token expiration tests
- ✅ Refresh token rotation tests

Target: >80% code coverage

## Next Steps (Phase 2)

1. **Exam Management**
   - Create/read/update/delete exams
   - Exam scheduling
   - Candidate enrollment

2. **Proctoring Features**
   - Video/audio monitoring
   - Screen recording
   - Behavioral analysis

3. **Evidence Management**
   - Evidence collection
   - Evidence review workflow
   - Evidence storage (S3/cloud)

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.
