# API Integration Guide

## WebSocket Connection

The Invigilator Dashboard connects to a WebSocket server for real-time updates.

### Connection Setup

```
Protocol: ws:// (or wss:// for HTTPS)
Host: {server-url}
Port: {server-port}
Path: /api/ws
```

### Message Types

#### 1. Alert Message
Sent when a new alert is generated.

```typescript
{
  type: 'alert',
  data: {
    id: 'alert-123',
    sessionId: 'session-001',
    type: 'mobile_phone' | 'face_not_visible' | 'multiple_faces' | 'copied_text' | 'tab_switch' | 'inactivity' | 'audio_anomaly' | 'manual',
    severity: 'low' | 'medium' | 'high' | 'critical',
    confidence: 0.95, // 0-1
    message: 'Mobile phone detected in frame [95% confidence]',
    timestamp: 1234567890,
    isAcknowledged: false,
    snapshot: 'data:image/jpeg;base64,...' // Optional
  }
}
```

#### 2. Score Update Message
Sent when risk score changes.

```typescript
{
  type: 'score_update',
  data: {
    sessionId: 'session-001',
    score: 65 // 0-100
  }
}
```

#### 3. Event Message
Sent when timeline event occurs.

```typescript
{
  type: 'event',
  data: {
    id: 'event-456',
    sessionId: 'session-001',
    eventType: 'face_not_visible',
    timestamp: 1234567890,
    confidence: 0.88, // 0-1
    riskContribution: 15, // Points added to risk
    snapshot: 'data:image/jpeg;base64,...',
    severity: 'high'
  }
}
```

#### 4. Session Update Message
Sent when session status changes.

```typescript
{
  type: 'session_update',
  data: {
    id: 'session-001',
    candidateId: 'candidate-001',
    candidateName: 'John Smith',
    sessionStartTime: 1234567890,
    currentRiskScore: 45,
    status: 'active' | 'paused' | 'flagged',
    videoStreamUrl: 'https://...',
    riskTrend: [10, 12, 15, 18, ...] // Array of recent scores
  }
}
```

#### 5. Connection Status Message
Sent on connection events.

```typescript
{
  type: 'connection',
  data: {
    status: 'connected' | 'disconnected' | 'reconnecting',
    message: 'Connected to server'
  }
}
```

### Client Messages

#### Acknowledge Alert
```typescript
{
  type: 'alert',
  data: {
    action: 'acknowledge',
    alertId: 'alert-123'
  }
}
```

#### Pause/Flag Session
```typescript
{
  type: 'session_update',
  data: {
    action: 'pause' | 'flag' | 'unflag' | 'resume',
    sessionId: 'session-001'
  }
}
```

#### Add Manual Note
```typescript
{
  type: 'alert',
  data: {
    action: 'add_note',
    sessionId: 'session-001',
    message: 'Candidate appeared distracted',
    severity: 'low' | 'medium' | 'high'
  }
}
```

## REST API Endpoints (Phase 2)

### Get Exam Information
```
GET /api/exams/{examId}
```

Response:
```json
{
  "id": "exam-001",
  "name": "Mathematics Final Exam",
  "startTime": 1234567890,
  "duration": 3600000,
  "totalCandidates": 50,
  "activeCandidates": 48
}
```

### Get Session Details
```
GET /api/sessions/{sessionId}
```

### Download Evidence
```
GET /api/evidence/{evidenceId}/download
```

### Get Event History
```
GET /api/sessions/{sessionId}/events?limit=100&offset=0
```

### Export Report
```
POST /api/exams/{examId}/export
```

## Error Handling

### WebSocket Errors
```typescript
{
  type: 'connection',
  data: {
    status: 'error',
    code: 'CONNECTION_FAILED',
    message: 'Failed to connect to server'
  }
}
```

### Reconnection Strategy
1. Attempt to reconnect after 3 seconds
2. Use exponential backoff: 3s, 6s, 12s, 30s, 60s
3. Maximum 10 reconnection attempts
4. Display warning after 5 failed attempts
5. Show error modal after all attempts exhausted

## Data Requirements

### Video Stream Format
- **Codec**: H.264 (video), AAC (audio)
- **Resolution**: 1920x1080 (HD) or 1280x720 (SD)
- **Frame Rate**: 25 fps or 30 fps
- **Bitrate**: 3-5 Mbps (HD) or 1-2 Mbps (SD)
- **Protocol**: HLS or DASH

### Evidence Image Format
- **Format**: JPEG or WebP
- **Resolution**: 1920x1080 minimum
- **Compression**: JPEG quality 85%
- **Size**: <500KB per image

## Performance Considerations

### Alert Volume
- Handle up to 100 alerts per session
- Auto-dismiss low priority after 30 seconds
- Keep last 500 alerts in history

### Event Timeline
- Store last 1000 events
- Paginate if exceeding 500 items
- Archive older events periodically

### Video Streams
- Support 10-50 concurrent streams
- Quality negotiation based on bandwidth
- Automatic fallback to lower quality

### Score Updates
- Send every 5-30 seconds
- Include trend data (last 30 points)
- Use delta encoding for compression

## Security

### WebSocket Authentication
- Include auth token in connection URL or header
- Validate token on each message
- Disconnect if token invalid or expired
- Refresh token on reconnection

### Data Encryption
- Use WSS (WebSocket Secure) for HTTPS
- Encrypt evidence snapshots
- Secure video stream transmission
- Hash sensitive candidate data

### Access Control
- Invigilators can only view assigned exams
- Verify sessionId ownership on updates
- Prevent cross-session tampering
- Log all sensitive actions

## Testing

### Mock WebSocket Server
```typescript
// For development/testing
const mockWs = new MockWebSocket({
  url: 'ws://localhost:3000/api/ws',
  autoRespond: true,
  delay: 100
});
```

### Example Test Data
See `/e2e/` directory for test fixtures and mock implementations.

## Troubleshooting

### Connection Won't Establish
1. Check server is running
2. Verify WebSocket URL is correct
3. Check firewall/proxy settings
4. Verify authentication token
5. Check browser console for errors

### Delayed Messages
1. Check network latency (cmd: `ping {server}`)
2. Verify server is not overloaded
3. Check message size (compress if large)
4. Review server logs for bottlenecks

### Missing Alerts/Events
1. Verify WebSocket is connected
2. Check browser dev tools for console errors
3. Verify message format from server
4. Check that timestamp parsing is correct

## Version History

### v1.0
- Initial release with core WebSocket messaging
- Support for alerts, events, and score updates
- Session management and pause/flag functionality

### v2.0 (Planned)
- RESTful API for historical data
- Advanced filtering and search
- Report generation and export
- Mobile client support

## Additional Resources

- [WebSocket API Reference](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Video.js Documentation](https://docs.videojs.com/)
- [HLS Streaming](https://developer.apple.com/streaming/)
- [WCAG 2.1 Accessibility](https://www.w3.org/WAI/WCAG21/quickref/)
