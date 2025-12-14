# WebSocket Message Protocol

This document describes the WebSocket message protocol used for communication between candidates, invigilators, and the server.

## Message Format

All WebSocket messages follow this JSON structure:

```json
{
  "type": "message_type",
  "data": {
    // Message-specific data
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Message Types

### Connection Messages

#### CONNECT
Sent when a connection is established.

**Direction:** Server → Client

```json
{
  "type": "connect",
  "data": {
    "message": "Connected successfully",
    "session_id": "session-123",
    "exam_id": "exam-001"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### DISCONNECT
Sent when a connection is closed.

**Direction:** Server → Client

```json
{
  "type": "disconnect",
  "data": {
    "reason": "Normal closure"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### PING / PONG
Heartbeat messages for connection health monitoring.

**Direction:** Bidirectional

```json
{
  "type": "ping",
  "data": {},
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

```json
{
  "type": "pong",
  "data": {},
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Permission Messages

#### PERMISSION_GRANTED
Sent when candidate grants media permissions.

**Direction:** Candidate → Server → Invigilator

```json
{
  "type": "permission_granted",
  "data": {},
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### PERMISSION_DENIED
Sent when candidate denies media permissions.

**Direction:** Candidate → Server → Invigilator

```json
{
  "type": "permission_denied",
  "data": {
    "reason": "User declined consent"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Media Stream Messages

#### VIDEO_FRAME
Video frame data encoded as base64 JPEG.

**Direction:** Candidate → Server → Invigilator

```json
{
  "type": "video_frame",
  "data": {
    "session_id": "session-123",
    "frame_data": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "frame_number": 42,
    "quality": "medium",
    "timestamp": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Fields:**
- `session_id`: Unique session identifier
- `frame_data`: Base64-encoded JPEG image
- `frame_number`: Sequential frame number
- `quality`: Video quality setting (low/medium/high)

#### AUDIO_CHUNK
Audio chunk data encoded as base64.

**Direction:** Candidate → Server → Invigilator

```json
{
  "type": "audio_chunk",
  "data": {
    "session_id": "session-123",
    "audio_data": "base64_encoded_audio_data",
    "chunk_number": 15,
    "sample_rate": 48000,
    "timestamp": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Fields:**
- `session_id`: Unique session identifier
- `audio_data`: Base64-encoded audio data
- `chunk_number`: Sequential chunk number
- `sample_rate`: Audio sample rate in Hz

### Status Messages

#### CANDIDATE_STATUS
Candidate's current status and capabilities.

**Direction:** Candidate → Server → Invigilator

```json
{
  "type": "candidate_status",
  "data": {
    "session_id": "session-123",
    "candidate_id": "candidate-456",
    "status": "streaming",
    "has_video": true,
    "has_audio": true,
    "network_quality": "good",
    "timestamp": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Status values:**
- `connecting`: Initial connection
- `permissions_granted`: Media permissions granted
- `streaming`: Actively streaming media
- `paused`: Streaming paused
- `disconnected`: Connection lost

**Network quality values:**
- `excellent`: >1000 kbps
- `good`: 500-1000 kbps
- `fair`: 200-500 kbps
- `poor`: <200 kbps

#### STREAM_QUALITY
Real-time stream quality metrics.

**Direction:** Candidate → Server → Invigilator

```json
{
  "type": "stream_quality",
  "data": {
    "session_id": "session-123",
    "video_quality": "medium",
    "fps": 10,
    "bandwidth_kbps": 750.5,
    "timestamp": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Alert Messages

#### ALERT
Alerts sent to invigilators about candidate activity.

**Direction:** Server → Invigilator

```json
{
  "type": "alert",
  "data": {
    "level": "warning",
    "message": "Candidate moved out of frame",
    "candidate_id": "candidate-456",
    "session_id": "session-123",
    "details": {
      "detection_type": "face_detection",
      "confidence": 0.95
    }
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Alert levels:**
- `info`: Informational message
- `warning`: Potential issue requiring attention
- `critical`: Serious violation requiring immediate action

**Direction:** Server → Candidate (Non-intrusive)

Candidates may receive non-intrusive alerts:

```json
{
  "type": "alert",
  "data": {
    "level": "info",
    "message": "Please ensure your face is clearly visible in the camera"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## WebSocket Endpoints

### Candidate Endpoint

```
WS /ws/candidate/{session_id}?exam_id={exam_id}
```

**Parameters:**
- `session_id` (path): Unique candidate session identifier
- `exam_id` (query, optional): Exam identifier for grouping

**Usage:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/candidate/session-123?exam_id=exam-001');
```

### Invigilator Endpoint

```
WS /ws/exam/{exam_id}?invigilator_id={invigilator_id}
```

**Parameters:**
- `exam_id` (path): Exam identifier
- `invigilator_id` (query): Invigilator identifier

**Usage:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/exam/exam-001?invigilator_id=inv-123');
```

## Connection Lifecycle

### 1. Connection Establishment

```
Client → Server: WebSocket handshake
Server → Client: CONNECT message
Client ↔ Server: PING/PONG heartbeat (every 30s)
```

### 2. Permission Request (Candidate)

```
Client → Server: PERMISSION_GRANTED or PERMISSION_DENIED
Server → Invigilators: Broadcast permission status
```

### 3. Media Streaming (Candidate)

```
Client → Server: VIDEO_FRAME (5-10 FPS)
Server → Invigilators: Broadcast video frames
Client → Server: AUDIO_CHUNK (real-time)
Server → Invigilators: Broadcast audio chunks
Client → Server: CANDIDATE_STATUS (periodic)
Server → Invigilators: Broadcast status updates
```

### 4. Monitoring (Invigilator)

```
Server → Invigilators: VIDEO_FRAME (from candidates)
Server → Invigilators: AUDIO_CHUNK (from candidates)
Server → Invigilators: CANDIDATE_STATUS updates
Server → Invigilators: ALERT messages
```

### 5. Disconnection

```
Client: Connection lost
Server → Other Clients: ALERT (candidate disconnected)
Server: Clean up connection state
```

## Error Handling

### Connection Errors

If a connection error occurs, the client should:
1. Attempt reconnection with exponential backoff
2. Maximum 5 reconnection attempts
3. Initial delay: 3 seconds
4. Max delay: 30 seconds

### Message Errors

Invalid JSON messages will receive an error response:

```json
{
  "type": "error",
  "data": {
    "message": "Invalid JSON format",
    "code": "PARSE_ERROR"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Best Practices

1. **Always validate message structure** before processing
2. **Handle reconnections gracefully** with exponential backoff
3. **Monitor heartbeat messages** to detect connection issues
4. **Implement message queuing** for offline/reconnection scenarios
5. **Compress large payloads** (especially video frames)
6. **Rate limit message sending** to prevent overwhelming the server
7. **Use WebSocket secure (wss://)** in production
8. **Implement proper error boundaries** in client code

## Security Considerations

1. **Authentication**: Validate session IDs and exam IDs
2. **Authorization**: Verify candidate/invigilator permissions
3. **Data Validation**: Sanitize all incoming data
4. **Rate Limiting**: Prevent DoS attacks
5. **Encryption**: Use WSS (WebSocket Secure) in production
6. **Message Integrity**: Validate message signatures if required
