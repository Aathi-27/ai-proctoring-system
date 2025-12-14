# AI-Powered Proctoring System

## Overview
This is an AI-Powered Proctoring System designed to provide secure and intelligent exam proctoring. It leverages real-time audio/video analysis to detect anomalies and ensure exam integrity.

## Tech Stack
- **Frontend:** Next.js 14, TypeScript, TailwindCSS, WebRTC, WebSockets
- **Backend:** FastAPI, SQLAlchemy, Motor (MongoDB async driver), Pydantic
- **Databases:** PostgreSQL (User/Exam data), MongoDB (Events/Logs)
- **Storage:** MinIO (S3-compatible)
- **Containerization:** Docker, Docker Compose
- **CI/CD:** GitHub Actions

## Architecture
The system consists of a Next.js frontend communicating with a FastAPI backend. PostgreSQL is used for relational data (users, exams), while MongoDB stores high-volume event logs and risk scores. MinIO is used for storing exam session recordings.

(Architecture Diagram Placeholder)

## Repository Structure
- `/frontend`: Next.js 14 application
- `/backend`: FastAPI application
- `/ai`: AI models and processing logic (To be implemented)
- `/docker`: Docker configuration
- `/tests`: System-wide tests
- `/docs`: Documentation

## Local Setup

### Prerequisites
- Docker and Docker Compose
- Node.js (for local frontend development without Docker)
- Python 3.11+ (for local backend development without Docker)

### Running with Docker Compose
1. Clone the repository.
2. Create `.env` file from example:
   ```bash
   cp .env.example .env
   ```
3. Build and start services:
   ```bash
   docker-compose up --build
   ```
   This will start:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - MinIO Console: http://localhost:9001
   - Postgres, MongoDB, Redis

### Database Initialization
The database schema is initialized automatically by the backend service. For MongoDB collections, they are initialized when the application starts or via the initialization script.

To manually run initialization:
```bash
docker-compose exec backend python app/init_db.py
```

## Development Workflow
- **Frontend:**
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
- **Backend:**
  ```bash
  cd backend
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  uvicorn main:app --reload
  ```

## CI/CD
The project uses GitHub Actions for CI/CD:
- **Linting:** Black (Python), ESLint (TS)
- **Testing:** Pytest (Backend), Jest (Frontend)
- **Build:** Docker image build validation
