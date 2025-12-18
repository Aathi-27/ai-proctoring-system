# Implementation Summary: Exam Proctoring System

## Overview

This document summarizes the implementation of the Exam Proctoring platform, including Authentication, User Management, WebRTC Media Capture, WebSocket Infrastructure, and Face Detection/Liveness.

## ✅ Completed Features

### 1. User Roles Implementation
- ✅ **Candidate**: Can take exams, view own evidence
- ✅ **Invigilator**: Can monitor assigned exams
- ✅ **Admin**: Full system access, user management
- ✅ **System Integrator**: API access, system integrations

All roles are implemented as an Enum in `backend/app/db/models.py` with proper database constraints.

### 2. JWT Token Generation and Validation
- ✅ **Access Tokens**: 15-minute expiration
- ✅ **Refresh Tokens**: 7-day expiration
- ✅ **Token Claims**: Include user_id, role, and exam_id (for future Phase 2)
- ✅ **Token Types**: Distinct "access" and "refresh" type claims
- ✅ **Security**: HS256 algorithm with configurable secret key

Implementation: `backend/app/core/security.py`

### 3. Authentication Endpoints
- ✅ **POST /auth/register**: Register new user (Candidate, Admin)
- ✅ **POST /auth/login**: JWT token generation
- ✅ **POST /auth/refresh**: Refresh token exchange with automatic revocation
- ✅ **POST /auth/logout**: Token invalidation
- ✅ **GET /auth/me**: Current user info

Implementation: `backend/app/api/v1/endpoints/auth.py`

### 4. RBAC Middleware
- ✅ **Route Protection**: `get_current_user` dependency
- ✅ **Role-Based Access**: `RoleChecker` class and `require_roles` helper
- ✅ **Token Validation**: Automatic Bearer token extraction and validation
- ✅ **User Status Check**: Active user verification
- ✅ **Exam-Scoped Access**: Infrastructure ready (Phase 2 feature)
- ✅ **Evidence Access Control**: Role-based filtering (Phase 2 feature)

Implementation: `backend/app/middleware/auth.py`

### 5. WebRTC Media Capture
- ✅ Browser requests microphone + camera permissions
- ✅ MediaStream capture with graceful fallback
- ✅ Error handling for permission denials and device unavailability
- ✅ Video stream display in candidate UI
- ✅ Audio stream processed and visualized

### 6. WebSocket Server (FastAPI)
- ✅ FastAPI WebSocket endpoints:
  - `/ws/exam/{exam_id}` — invigilator real-time feed
  - `/ws/candidate/{session_id}` — candidate alerts
- ✅ Connection management (connect, disconnect, reconnect logic)
- ✅ Message broadcasting to invigilators monitoring same exam
- ✅ Graceful connection degradation with auto-reconnect

### 7. Frontend WebRTC Integration (Next.js)
- ✅ Permission request UI with clear explanations
- ✅ Mandatory consent banner before exam start
- ✅ Local video preview (candidate sees themselves)
- ✅ Audio level visualization
- ✅ Connection status indicator

### 8. Media Stream Transmission
- ✅ Video frames encoded and sent to backend (configurable FPS: 5-15)
- ✅ Audio chunks streamed in real-time
- ✅ Bandwidth optimization (configurable quality settings)

### 9. Face Detection (MediaPipe)
- ✅ **Continuous face detection** from video frames with real-time processing (<500ms latency)
- ✅ **Confidence scores** for each detected face (0-1 range)
- ✅ **Face bounding boxes** with precise pixel coordinates
- ✅ **468 facial landmarks** per face (MediaPipe Face Mesh)
- ✅ **68-point face outline** extraction for compatibility
- ✅ **CPU-optimized** for 5-10 FPS input processing
- ✅ **Multiple face detection** capability (up to 5 faces configurable)

### 10. Multiple Face Detection & Alerts
- ✅ Alert triggered when 2+ faces detected in frame
- ✅ `MULTIPLE_PERSONS` event emitted with:
  - Face count
  - Confidence scores for all faces
  - Timestamp
  - Risk score contribution (+20 points)
- ✅ Logged to MongoDB events collection

### 11. Candidate Leaving Frame Detection
- ✅ Tracks when face disappears from view
- ✅ Alert after >5 seconds threshold (configurable)
- ✅ `FACE_NOT_DETECTED` event emitted with:
  - Duration in seconds
  - Timestamp
  - Risk score contribution (+20 points)
- ✅ Automatic resume when face reappears

### 12. Liveness Verification (Phase-1)

#### Blink Detection
- ✅ **Eye Aspect Ratio (EAR)** method implementation
- ✅ Monitors 6 landmarks per eye
- ✅ Detects eye closure/opening sequences within 5-10 frames
- ✅ Left/right eye independent tracking
- ✅ False positive prevention with temporal filtering (>0.3s between blinks)
- ✅ Threshold: EAR < 0.2 (configurable)

#### Movement Detection
- ✅ **Head Pose Estimation** using PnP algorithm
- ✅ Tracks yaw, pitch, and roll angles
- ✅ Detects significant movement (>10° threshold)
- ✅ Maintains pose history per exam session
- ✅ Calculates pose change deltas

#### Liveness Scoring (0-100)
- ✅ Blink count contribution: up to 50 points
- ✅ Movement events contribution: up to 50 points
- ✅ Requires BOTH blinks AND movement for "live" status
- ✅ Time window: 30 seconds (configurable)
- ✅ Real-time score updates

## Technical Implementation

### Backend Architecture

**Technology Stack:**
- FastAPI 0.109.0 for async WebSocket support
- Uvicorn ASGI server
- Pydantic v2 for data validation
- Python 3.9+ with async/await
- PostgreSQL for user data
- MongoDB for event logs
- MediaPipe 0.10.14: Face detection and landmark extraction
- OpenCV 4.12: Image processing
- NumPy 2.2: Numerical computations

**Key Components:**
1. **ConnectionManager** (`app/websocket/connection_manager.py`)
   - Manages active WebSocket connections
   - Handles exam rooms (grouping candidates by exam)
   - Broadcasting to specific groups

2. **WebSocket Endpoints** (`app/websocket/endpoints.py`)
   - Candidate endpoint: `/ws/candidate/{session_id}?exam_id={exam_id}`
   - Invigilator endpoint: `/ws/exam/{exam_id}?invigilator_id={invigilator_id}`

3. **Face Detection Service** (`app/services/face_detection.py`)
   - MediaPipe integration
   - Liveness detection logic
   - Event emission

### Frontend Architecture

**Technology Stack:**
- Next.js 14 with App Router
- TypeScript 5.3.3 (strict mode)
- React 18.2.0 (functional components + hooks)
- Native WebRTC APIs
- Native WebSocket API

## WebSocket Message Protocol

### Message Format
```json
{
  "type": "message_type",
  "data": { /* message-specific data */ },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Key Message Types
- `connect` / `disconnect` - Connection lifecycle
- `ping` / `pong` - Heartbeat
- `permission_granted` / `permission_denied` - Permission status
- `video_frame` - Video frame data (base64 JPEG)
- `audio_chunk` - Audio chunk data
- `candidate_status` - Candidate streaming status
- `stream_quality` - Quality metrics
- `alert` - Alerts to invigilators
- `face_detected` - Face analysis results
