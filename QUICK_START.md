# Quick Start Guide

This guide will help you get the Exam Proctoring System authentication system up and running quickly.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

## Quick Setup (5 minutes)

### 1. Start PostgreSQL Database

```bash
docker-compose up -d
```

Wait a few seconds for PostgreSQL to start.

### 2. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run Backend Server

```bash
cd app
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### 4. Setup Frontend (New Terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

## Testing the System

### 1. Register a New User

Open http://localhost:3000 and click "Register"

- **Email**: test@example.com
- **Password**: TestPass123! (min 8 characters)
- **Full Name**: Test User
- **Role**: Candidate or Admin

### 2. Login

After registration, you'll be redirected to the login page. Login with your credentials.

### 3. Access Dashboard

After successful login, you'll see the dashboard with your user information.

## API Testing with curl

### Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "api@example.com",
    "password": "SecurePass123!",
    "full_name": "API Test User",
    "role": "candidate"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "api@example.com",
    "password": "SecurePass123!"
  }'
```

Save the `access_token` from the response.

### Get Current User

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest
```

For coverage report:

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in your browser
```

## Stopping the System

1. Stop the backend: Press `Ctrl+C` in the terminal
2. Stop the frontend: Press `Ctrl+C` in the terminal
3. Stop PostgreSQL: `docker-compose down`

## Default Test Users

The system doesn't come with pre-created users. You need to register users through:
1. The registration endpoint (`/api/v1/auth/register`) for Candidates and Admins
2. The user management endpoints (`/api/v1/users/`) for other roles (requires Admin access)

## Troubleshooting

### Database Connection Error

Make sure PostgreSQL is running:
```bash
docker-compose ps
```

If not running, start it:
```bash
docker-compose up -d
```

### Port Already in Use

- Backend (8000): Change port in uvicorn command: `uvicorn main:app --reload --port 8001`
- Frontend (3000): Change port: `PORT=3001 npm run dev`
- PostgreSQL (5432): Change port in `docker-compose.yml`

### Module Not Found Error

Make sure you're in the right directory and virtual environment is activated:
```bash
cd backend
source venv/bin/activate
cd app
```

## Next Steps

- Read the full README.md for detailed documentation
- Explore the API documentation at http://localhost:8000/docs
- Run the test suite to understand system behavior
- Review the code to understand the authentication flow
