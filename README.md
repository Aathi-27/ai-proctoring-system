# AI-Powered Proctoring System

## Overview
This is an AI-Powered Proctoring System designed to provide secure and intelligent exam proctoring. It leverages real-time audio/video analysis to detect anomalies and ensure exam integrity.

## Features
- **Authentication:** JWT-based auth with RBAC (Candidate, Invigilator, Admin)
- **Monitoring:** Real-time face detection, object detection, voice activity detection
- **Security:** Secure browser monitoring, screen analysis

## Tech Stack
- **Frontend:** Next.js 14, TypeScript, TailwindCSS, WebRTC, WebSockets
- **Backend:** FastAPI, SQLAlchemy, Motor (MongoDB async driver), Pydantic
- **Databases:** PostgreSQL (User/Exam data), MongoDB (Events/Logs)
- **Storage:** MinIO (S3-compatible)
- **Containerization:** Docker, Docker Compose
- **CI/CD:** GitHub Actions

## Architecture
The system consists of a Next.js frontend communicating with a FastAPI backend. PostgreSQL is used for relational data (users, exams), while MongoDB stores high-volume event logs and risk scores. MinIO is used for storing exam session recordings.

## Repository Structure
- `/frontend`: Next.js 14 application
- `/backend`: FastAPI application
- `/ai`: AI models and processing logic
- `/docker`: Docker configuration
- `/tests`: System-wide tests
- `/docs`: Documentation

## Local Setup

### Known Browser Limitations
- **Browser-only monitoring**: The system relies on browser APIs (WebRTC) and cannot monitor full OS-level activity or other applications.
- **Background tab detection**: Detection of tab switching is "best-effort" using the Page Visibility API and may be circumvented.
- **No OS hooks**: We do not install any software on the candidate's machine, so we cannot lock down the computer.

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

   **Note:** The `.env.example` sets `NEXT_PUBLIC_API_URL=http://backend:8000` for Docker networking. If you are running the frontend locally (outside Docker) but accessing the backend in Docker, you may need to set this to `http://localhost:8000`.

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
