<<<<<<< HEAD
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
=======
# Online Exam Proctoring - WebRTC & WebSocket Infrastructure

Real-time media capture and WebSocket infrastructure for secure online examination proctoring.

## 🚀 Features

### WebRTC Media Capture
- ✅ Browser-based webcam and microphone access
- ✅ Real-time video and audio streaming
- ✅ Configurable quality levels (low/medium/high)
- ✅ Adaptive frame rate (5-15 FPS)
- ✅ Permission handling with retry logic
- ✅ Device error handling and fallbacks
- ✅ Local video preview for candidates
- ✅ Audio level visualization

### WebSocket Communication
- ✅ Real-time bidirectional communication
- ✅ FastAPI WebSocket endpoints
- ✅ Connection management (connect/disconnect/reconnect)
- ✅ Message broadcasting to exam rooms
- ✅ Automatic reconnection with exponential backoff
- ✅ Heartbeat mechanism (ping/pong)
- ✅ Graceful degradation on connection loss

### User Experience
- ✅ Mandatory consent banner before streaming
- ✅ Clear permission request UI
- ✅ Connection status indicator
- ✅ Non-intrusive alerts for candidates
- ✅ Real-time monitoring dashboard for invigilators
- ✅ Video preview with live indicator
- ✅ Audio level monitoring

### Security & Privacy
- ✅ Mandatory consent before data collection
- ✅ Clear privacy explanations
- ✅ HTTPS required for production
- ✅ No data retention (Phase 1)
- ✅ Privacy-by-design approach

## 📁 Project Structure

```
.
├── backend/                  # FastAPI WebSocket server
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models/          # Pydantic models
│   │   │   └── websocket_models.py
│   │   └── websocket/       # WebSocket endpoints
│   │       ├── connection_manager.py
│   │       └── endpoints.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                 # Next.js frontend
│   ├── app/                 # Next.js app directory
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── candidate/       # Candidate exam interface
│   │   │   └── [session_id]/
│   │   │       └── page.tsx
│   │   └── invigilator/     # Invigilator monitoring interface
│   │       └── [exam_id]/
│   │           └── page.tsx
│   ├── components/          # React components
│   │   ├── ConsentBanner.tsx
│   │   ├── VideoPreview.tsx
│   │   ├── AudioLevelVisualizer.tsx
│   │   ├── ConnectionStatus.tsx
│   │   └── MediaCapture.tsx
│   ├── hooks/               # Custom React hooks
│   │   ├── useWebRTC.ts
│   │   └── useWebSocket.ts
│   ├── lib/                 # Utility libraries
│   │   ├── webrtc.ts
│   │   └── websocket.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
│
├── docs/                    # Documentation
│   ├── WEBSOCKET_PROTOCOL.md
│   ├── MEDIA_ENCODING.md
│   └── BROWSER_COMPATIBILITY.md
│
├── .gitignore
└── README.md
```

## 🛠️ Setup & Installation

### Prerequisites

- **Backend**: Python 3.9+, pip
- **Frontend**: Node.js 18+, npm
- **Development**: HTTPS (or localhost for testing)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend server will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🎯 Usage

### Candidate Flow

1. Navigate to `/candidate/{session_id}?exam_id={exam_id}`
2. Review and accept the consent banner
3. Grant camera and microphone permissions
4. Video preview and audio level indicator will appear
5. Media streams automatically to the backend
6. Connection status is displayed in real-time

**Example URL:**
```
http://localhost:3000/candidate/session-123?exam_id=exam-001
```

### Invigilator Flow

1. Navigate to `/invigilator/{exam_id}?invigilator_id={invigilator_id}`
2. WebSocket connection establishes automatically
3. View all active candidates in the exam
4. Monitor video feeds in real-time
5. Receive alerts about candidate activity
6. Connection status is displayed in real-time

**Example URL:**
```
http://localhost:3000/invigilator/exam-001?invigilator_id=inv-123
```

## 📡 WebSocket Endpoints

### Candidate Endpoint
```
WS /ws/candidate/{session_id}?exam_id={exam_id}
```

Connects a candidate to the exam session for media streaming.

### Invigilator Endpoint
```
WS /ws/exam/{exam_id}?invigilator_id={invigilator_id}
```

Connects an invigilator to monitor all candidates in an exam.

## 📨 Message Protocol

### Video Frame Message
```json
{
  "type": "video_frame",
  "data": {
    "session_id": "session-123",
    "frame_data": "data:image/jpeg;base64,...",
    "frame_number": 42,
    "quality": "medium"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Candidate Status Message
```json
{
  "type": "candidate_status",
  "data": {
    "session_id": "session-123",
    "status": "streaming",
    "has_video": true,
    "has_audio": true,
    "network_quality": "good"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

See [WEBSOCKET_PROTOCOL.md](docs/WEBSOCKET_PROTOCOL.md) for complete protocol specification.

## 🎨 Components

### ConsentBanner
Displays mandatory consent banner before media access.

### MediaCapture
Main component handling WebRTC capture and WebSocket streaming.

### VideoPreview
Displays local video preview with live indicator.

### AudioLevelVisualizer
Real-time audio level visualization.

### ConnectionStatus
WebSocket connection status indicator.

## 🔧 Configuration

### Backend Configuration

Environment variables:
```bash
CORS_ORIGINS=*  # Configure CORS origins
LOG_LEVEL=INFO  # Logging level
```

### Frontend Configuration

Environment variables (`.env.local`):
```bash
NEXT_PUBLIC_WS_URL=ws://localhost:8000  # WebSocket server URL
```

### Video Quality Settings

```typescript
// Low quality
{ videoQuality: 'low', fps: 5 }  // ~50-100 kbps

// Medium quality (default)
{ videoQuality: 'medium', fps: 10 }  // ~150-300 kbps

// High quality
{ videoQuality: 'high', fps: 15 }  // ~500-800 kbps
```

## 🌐 Browser Compatibility

| Browser | Version | Support | Notes |
|---------|---------|---------|-------|
| Chrome | 74+ | ✅ Full | Recommended |
| Firefox | 66+ | ✅ Full | Excellent |
| Edge | 79+ | ✅ Full | Chromium |
| Safari | 12+ | ⚠️ Partial | HTTPS required |

See [BROWSER_COMPATIBILITY.md](docs/BROWSER_COMPATIBILITY.md) for detailed compatibility information.

## 📚 Documentation

- [WebSocket Protocol](docs/WEBSOCKET_PROTOCOL.md) - Message format and protocol specification
- [Media Encoding](docs/MEDIA_ENCODING.md) - Video and audio encoding specifications
- [Browser Compatibility](docs/BROWSER_COMPATIBILITY.md) - Browser support matrix and considerations

## 🧪 Testing

### Backend Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Manual Testing

1. Start both backend and frontend servers
2. Open candidate page in one browser tab
3. Open invigilator page in another tab
4. Grant permissions on candidate page
5. Verify video stream appears on invigilator page
6. Test connection by refreshing pages
7. Verify reconnection logic

## 🚀 Deployment

### Backend Deployment

```bash
# Production mode with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Requirements:**
- HTTPS with valid SSL certificate
- WebSocket support on load balancer
- Proper CORS configuration

### Frontend Deployment

```bash
# Build for production
npm run build

# Start production server
npm start
```

**Requirements:**
- HTTPS with valid SSL certificate
- WebSocket URL pointing to backend
- Proper environment variables

### Docker Deployment (Optional)

```dockerfile
# Backend Dockerfile
FROM python:3.9
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend Dockerfile
FROM node:18
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build
CMD ["npm", "start"]
```

## 🔒 Security Considerations

1. **HTTPS Required**: WebRTC requires HTTPS in production (except localhost)
2. **Authentication**: Implement proper authentication (not included in Phase 1)
3. **Authorization**: Validate session IDs and exam IDs
4. **Rate Limiting**: Prevent DoS attacks on WebSocket endpoints
5. **Data Validation**: Sanitize all incoming messages
6. **CORS Configuration**: Restrict origins in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is part of an online exam proctoring system implementation.

## 🙏 Acknowledgments

- FastAPI for the excellent async WebSocket support
- Next.js for the modern React framework
- WebRTC community for browser media APIs

## 📧 Support

For issues and questions:
- Check the documentation in the `docs/` directory
- Review browser compatibility matrix
- Test with recommended browsers first

---

**Phase 1 Deliverables:** ✅ Complete
- WebRTC media capture with permission handling
- WebSocket server with real-time communication
- Frontend components with consent flow
- Video/audio streaming infrastructure
- Comprehensive documentation
>>>>>>> origin/feature/webrtc-media-capture-websocket-fastapi
