# WebSocket Alert System Documentation

## Overview

This document describes the WebSocket-based real-time alert system for invigilators monitoring AI proctoring exams. The system provides real-time event broadcasting, evidence capture, and alert management capabilities.

## WebSocket Message Protocol

### Connection Establishment

**Endpoint**: `ws://localhost:8000/api/v1/ws/exam/{exam_id}`

**Connection URL Parameters**:
- `invigilator_id` (required): Unique identifier for the invigilator
- `last_message_id` (optional): For reconnection scenarios

**Example Connection**:
```javascript
const websocket = new WebSocket('ws://localhost:8000/api/v1/ws/exam/exam_123?invigilator_id=invigilator_456');
```

### Message Format

All messages are JSON-encoded and include common fields:
- `type`: Message type identifier
- `message_id`: Unique message identifier for ordering
- `server_timestamp`: Server timestamp in ISO 8601 format

### Message Types

#### 1. Connection Established
**Direction**: Server → Client
**Purpose**: Confirmation of successful connection

```json
{
  "type": "connection_established",
  "connection_id": "invigilator_456_1642247032.123",
  "timestamp": "2025-01-15T14:23:45.123Z",
  "message_id": "msg_1_1642247032.123",
  "server_timestamp": "2025-01-15T14:23:45.123Z"
}
```

#### 2. Alert Notification
**Direction**: Server → Client
**Purpose**: Real-time alert broadcast

```json
{
  "type": "alert",
  "message_id": "msg_2_1642247033.456",
  "server_timestamp": "2025-01-15T14:23:46.456Z",
  "alert": {
    "alert_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "exam_id": "exam_123",
    "session_id": "session_456",
    "timestamp": "2025-01-15T14:23:46.456Z",
    "event_type": "MOBILE_DETECTED",
    "severity": "CRITICAL",
    "confidence": 0.95,
    "risk_score_delta": 25,
    "current_risk_score": 50,
    "message": "Mobile phone detected in camera frame",
    "evidence_snapshot_id": "snapshot_789",
    "acknowledged": false
  }
}
```

#### 3. Acknowledgment Request
**Direction**: Client → Server
**Purpose**: Acknowledge alert receipt

```json
{
  "type": "acknowledge_alert",
  "alert_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message_id": "msg_3_1642247034.789",
  "timestamp": "2025-01-15T14:23:47.789Z"
}
```

#### 4. Acknowledgment Response
**Direction**: Server → Client
**Purpose**: Confirm alert acknowledgment

```json
{
  "type": "acknowledgment",
  "alert_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "success": true,
  "timestamp": "2025-01-15T14:23:47.890Z",
  "message_id": "msg_4_1642247034.890",
  "server_timestamp": "2025-01-15T14:23:47.890Z"
}
```

#### 5. Alert History Request
**Direction**: Client → Server
**Purpose**: Request historical alerts

```json
{
  "type": "get_alerts",
  "session_id": "session_456",
  "severity": "CRITICAL",
  "event_type": "MOBILE_DETECTED",
  "limit": 50,
  "offset": 0,
  "message_id": "msg_5_1642247035.123",
  "timestamp": "2025-01-15T14:23:48.123Z"
}
```

#### 6. Alert History Response
**Direction**: Server → Client
**Purpose**: Return historical alerts

```json
{
  "type": "alert_history",
  "message_id": "msg_6_1642247035.234",
  "server_timestamp": "2025-01-15T14:23:48.234Z",
  "alerts": [
    {
      "alert_id": "alert_1",
      "exam_id": "exam_123",
      "session_id": "session_456",
      "timestamp": "2025-01-15T14:23:46.456Z",
      "event_type": "MOBILE_DETECTED",
      "severity": "CRITICAL",
      "confidence": 0.95,
      "risk_score_delta": 25,
      "current_risk_score": 50,
      "message": "Mobile phone detected in camera frame",
      "acknowledged": true,
      "acknowledged_by": "invigilator_456",
      "acknowledged_at": "2025-01-15T14:23:47.890Z"
    }
  ],
  "count": 1
}
```

#### 7. Ping/Pong (Heartbeat)
**Direction**: Client → Server (Ping)
**Direction**: Server → Client (Pong)
**Purpose**: Connection health monitoring

**Ping**:
```json
{
  "type": "ping",
  "timestamp": "2025-01-15T14:23:49.123Z"
}
```

**Pong**:
```json
{
  "type": "pong",
  "timestamp": "2025-01-15T14:23:49.234Z",
  "message_id": "msg_7_1642247036.234",
  "server_timestamp": "2025-01-15T14:23:49.234Z"
}
```

#### 8. Error Message
**Direction**: Server → Client
**Purpose**: Error notification

```json
{
  "type": "error",
  "message": "Invalid JSON format",
  "message_id": "msg_8_1642247036.345",
  "server_timestamp": "2025-01-15T14:23:49.345Z"
}
```

#### 9. Reconnection Request
**Direction**: Server → Client
**Purpose**: Request client to resend missed messages

```json
{
  "type": "resync_request",
  "last_message_id": "msg_5_1642247035.123",
  "timestamp": "2025-01-15T14:23:50.456Z",
  "message_id": "msg_9_1642247037.456",
  "server_timestamp": "2025-01-15T14:23:50.456Z"
}
```

## Alert Severity Levels

### Severity Hierarchy

1. **EMERGENCY** (Level 4)
2. **CRITICAL** (Level 3)
3. **WARNING** (Level 2)
4. **INFO** (Level 1)

### Severity Details

#### EMERGENCY
- **Color Code**: Red
- **Priority**: Highest
- **Response Time**: Immediate
- **Sound**: Continuous alarm
- **Examples**:
  - Security breach detected
  - Multiple serious violations
  - System failure during critical exam period

#### CRITICAL
- **Color Code**: Red
- **Priority**: High
- **Response Time**: < 30 seconds
- **Sound**: Alert sound
- **Event Types**:
  - `MOBILE_DETECTED`: Mobile phone in camera frame
  - `MULTIPLE_FACES`: Multiple people detected
  - `BACKGROUND_SPEECH`: Unauthorized background speech

#### WARNING
- **Color Code**: Yellow
- **Priority**: Medium
- **Response Time**: < 2 minutes
- **Sound**: Soft notification
- **Event Types**:
  - `TAB_SWITCH`: Tab switch during exam
  - `INACTIVITY`: Extended user inactivity
  - `FACE_NOT_DETECTED`: Face not detected for extended period

#### INFO
- **Color Code**: Green/Blue
- **Priority**: Low
- **Response Time**: No response required
- **Sound**: None
- **Event Types**:
  - `LIVENESS_CONFIRMED`: Liveness verification successful
  - `NORMAL_ACTIVITY`: Normal exam activity
  - `EXAM_STARTED`: Exam session started
  - `EXAM_ENDED`: Exam session ended

## Reconnection Behavior

### Automatic Reconnection

The system implements automatic reconnection with exponential backoff:

1. **Initial Connection Attempt**: Immediate
2. **First Retry**: 1 second after failure
3. **Second Retry**: 2 seconds after failure
4. **Third Retry**: 4 seconds after failure
5. **Subsequent Retries**: 8 seconds (maximum)

### Message Resumption

When a client reconnects, it can request missed messages by including `last_message_id` in the connection URL:

```javascript
const websocket = new WebSocket(
  'ws://localhost:8000/api/v1/ws/exam/exam_123?invigilator_id=invigilator_456&last_message_id=msg_10'
);
```

### Connection State Management

- **Connected**: Active WebSocket connection
- **Reconnecting**: Attempting to reconnect after disconnection
- **Disconnected**: No active connection
- **Error**: Connection error state

### Graceful Degradation

If WebSocket connection is lost:
1. Critical alerts may be cached for retry
2. Alert history remains accessible via REST API
3. Invigilators can reconnect to receive buffered alerts
4. System continues monitoring and generating alerts

## Evidence Snapshot Retention Policy

### Storage Configuration

- **Storage Backend**: MinIO (S3-compatible) or local filesystem fallback
- **Encryption**: AES-256 encryption at rest
- **Default Retention**: 30 days
- **Storage Path**: `{bucket}/evidence/{exam_id}/{session_id}/{snapshot_id}.jpg`

### Retention Schedule

#### Default Retention (30 days)
```yaml
evidence_retention:
  default: 30  # days
  configurable: true
  min: 1       # days
  max: 365     # days
```

#### Retention by Alert Severity
- **EMERGENCY**: 365 days
- **CRITICAL**: 90 days
- **WARNING**: 30 days
- **INFO**: 7 days

### Evidence Metadata

Each snapshot includes metadata:

```json
{
  "snapshot_id": "snapshot_789",
  "exam_id": "exam_123",
  "session_id": "session_456",
  "alert_id": "alert_456",
  "timestamp": "2025-01-15T14:23:46.456Z",
  "event_type": "MOBILE_DETECTED",
  "frame_number": 42,
  "risk_score": 50,
  "file_path": "evidence/exam_123/session_456/snapshot_789.jpg",
  "file_size": 1024,
  "encryption_key_id": "evidence_key_1",
  "retention_expires_at": "2025-02-14T14:23:46.456Z"
}
```

### Automated Cleanup

- **Frequency**: Daily at 2:00 AM UTC
- **Process**: 
  1. Query MongoDB for expired snapshots
  2. Delete from storage backend
  3. Remove metadata from database
  4. Log cleanup activities

### Security Considerations

1. **Encryption**: All snapshots encrypted with AES-256
2. **Access Control**: Role-based access to evidence
3. **Audit Trail**: All access logged
4. **Secure Transmission**: HTTPS/WSS for all communications
5. **Key Management**: Encryption keys rotated regularly

## API Endpoints

### Alert Management

#### GET `/api/v1/exams/{exam_id}/alerts`
Retrieve alert history for an exam.

**Parameters**:
- `session_id` (optional): Filter by session
- `severity` (optional): Filter by severity
- `event_type` (optional): Filter by event type
- `limit` (optional): Number of alerts (default: 100, max: 1000)
- `offset` (optional): Pagination offset (default: 0)

#### GET `/api/v1/exams/{exam_id}/alerts/{alert_id}`
Get specific alert by ID.

#### POST `/api/v1/exams/{exam_id}/alerts/{alert_id}/acknowledge`
Acknowledge an alert.

**Body**:
```json
{
  "alert_id": "alert_123",
  "invigilator_id": "invigilator_456"
}
```

#### GET `/api/v1/exams/{exam_id}/alerts/critical-count`
Get count of unacknowledged critical alerts.

#### GET `/api/v1/exams/{exam_id}/risk-score`
Get current risk score for an exam.

### Exam Monitoring

#### POST `/api/v1/exams/{exam_id}/monitoring/start`
Start exam monitoring session.

**Body**:
```json
{
  "session_id": "session_456"
}
```

#### POST `/api/v1/exams/{exam_id}/monitoring/end`
End exam monitoring session.

**Body**:
```json
{
  "session_id": "session_456"
}
```

### Connection Management

#### GET `/api/v1/exams/{exam_id}/invigilators`
Get list of connected invigilators.

#### GET `/api/v1/ws/health`
WebSocket service health check.

## Configuration

### Environment Variables

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=ai_proctoring

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false

# Evidence Encryption
EVIDENCE_ENCRYPTION_KEY=your_encryption_key_here

# WebSocket Configuration
WS_MAX_CONNECTIONS=1000
WS_MESSAGE_TIMEOUT=30

# Alert Configuration
ALERT_RETENTION_DAYS=30
ALERT_BATCH_SIZE=100
ALERT_PROCESSING_INTERVAL=1
```

### WebSocket Configuration

```python
# Connection Limits
MAX_CONNECTIONS_PER_EXAM = 50
MAX_TOTAL_CONNECTIONS = 1000

# Message Limits
MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10MB
MESSAGE_RATE_LIMIT = 100  # messages per minute

# Timeouts
CONNECTION_TIMEOUT = 30  # seconds
MESSAGE_ACK_TIMEOUT = 10  # seconds
PING_INTERVAL = 30  # seconds
```

## Monitoring and Metrics

### Key Metrics

1. **Connection Metrics**:
   - Active connections per exam
   - Connection success/failure rates
   - Average connection duration
   - Reconnection success rate

2. **Message Metrics**:
   - Messages sent/received per second
   - Message delivery success rate
   - Average message latency
   - Message queue size

3. **Alert Metrics**:
   - Alerts generated per minute
   - Alert acknowledgment rate
   - Critical alert response time
   - Evidence snapshot success rate

### Health Checks

- **Database**: MongoDB connection status
- **Storage**: MinIO connectivity and capacity
- **WebSocket**: Connection manager status
- **Alert Service**: Alert processing status

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if server is running
   - Verify WebSocket endpoint URL
   - Check firewall settings

2. **Messages Not Received**
   - Verify connection status
   - Check message filtering
   - Review browser console for errors

3. **High Latency**
   - Monitor server load
   - Check network connectivity
   - Review message queue sizes

4. **Evidence Not Captured**
   - Verify MinIO connection
   - Check storage permissions
   - Review encryption key configuration

### Log Levels

- **ERROR**: System errors and exceptions
- **WARNING**: Non-critical issues
- **INFO**: Normal operation events
- **DEBUG**: Detailed debugging information

## Best Practices

### Client Implementation

1. **Connection Management**:
   - Implement exponential backoff for reconnection
   - Handle connection state changes
   - Send periodic ping messages

2. **Message Handling**:
   - Process messages asynchronously
   - Implement message deduplication
   - Handle large messages gracefully

3. **Error Handling**:
   - Implement comprehensive error handling
   - Log errors for debugging
   - Provide user feedback for critical issues

### Server Management

1. **Resource Management**:
   - Monitor connection limits
   - Implement connection cleanup
   - Scale horizontally for high load

2. **Security**:
   - Validate all inputs
   - Implement rate limiting
   - Use secure WebSocket connections (WSS)

3. **Monitoring**:
   - Set up comprehensive logging
   - Monitor key metrics
   - Implement alerting for system issues