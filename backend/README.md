# Online Exam Proctoring - Backend

FastAPI-based WebSocket server for real-time media streaming and event handling.

## Features

- WebSocket endpoints for invigilators and candidates
- Real-time message broadcasting
- Connection management with automatic reconnection support
- Ping/pong heartbeat mechanism
- Video frame and audio chunk streaming
- Alert system for exam monitoring

## Setup

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Server

Development mode:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### REST Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /stats` - Connection statistics

### WebSocket Endpoints

#### Invigilator Connection
```
WS /ws/exam/{exam_id}?invigilator_id={invigilator_id}
```

Connects an invigilator to monitor a specific exam. Receives real-time updates about all candidates in the exam.

#### Candidate Connection
```
WS /ws/candidate/{session_id}?exam_id={exam_id}
```

Connects a candidate to the exam session. Sends media streams and receives non-intrusive alerts.

## Message Protocol

See [WEBSOCKET_PROTOCOL.md](../docs/WEBSOCKET_PROTOCOL.md) for detailed message format specifications.

## Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   └── websocket_models.py # Pydantic models
│   └── websocket/
│       ├── connection_manager.py # Connection management
│       └── endpoints.py         # WebSocket endpoints
└── requirements.txt
```

## Configuration

Environment variables:
- `CORS_ORIGINS` - Allowed CORS origins (default: all)
- `LOG_LEVEL` - Logging level (default: INFO)

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Deployment

For production deployment:
1. Use a production ASGI server (uvicorn with workers)
2. Configure CORS origins appropriately
3. Use HTTPS (required for WebRTC)
4. Set up load balancing for horizontal scaling
5. Implement proper logging and monitoring

## Security Considerations

- HTTPS is mandatory for WebRTC in production
- Implement authentication/authorization (not included in Phase 1)
- Validate all incoming messages
- Rate limit connections to prevent DoS
- Sanitize data before broadcasting
