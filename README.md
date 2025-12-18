# Exam Activity Monitoring System

A comprehensive browser-level monitoring system for online exams that tracks tab switching, copy-paste events, and user inactivity using browser APIs and WebSocket communication.

## Features

### 🔍 Tab/Window Visibility Detection
- **Page Visibility API**: Detects when candidates switch away from the exam tab
- **Window focus tracking**: Captures alt-tab and window switching events
- **Event logging**: `TAB_SWITCHED` with timestamp and inactive duration
- **Cross-browser support**: Works on Chrome, Firefox, Safari, and Edge

### 📋 Copy-Paste Event Logging
- **Copy detection**: Intercepts Ctrl+C / Cmd+C events
- **Paste detection**: Intercepts Ctrl+V / Cmd+V events
- **Optional paste blocking**: Can disable paste functionality per exam
- **Privacy-first**: Only logs event occurrence and content length (in bytes), NOT actual content
- **Events**: `COPY_DETECTED` and `PASTE_DETECTED` with timestamp and content_length

### ⏱️ Keyboard & Mouse Inactivity Tracking
- **Keyboard monitoring**: Tracks keyboard activity via keydown/keyup events
- **Mouse monitoring**: Tracks mouse activity via mousemove/click events
- **Configurable threshold**: Default 30 seconds, adjustable per exam
- **Events**: `KEYBOARD_INACTIVITY` and `MOUSE_INACTIVITY` with duration_seconds
- **Activity resumption**: `ACTIVITY_RESUMED` event when user becomes active again

### 🔐 Privacy & Security
- **No content capture**: Clipboard content is NEVER captured or stored
- **No keystroke logging**: Only activity presence/absence is tracked
- **No screenshots**: System respects candidate privacy
- **Mandatory consent**: Consent banner displayed before exam starts
- **Transparent**: Candidates are informed of all monitoring activities

### 🌐 Real-time Communication
- **WebSocket integration**: Events sent to backend in real-time
- **Automatic reconnection**: Exponential backoff retry strategy
- **MongoDB storage**: All events persisted with server timestamps
- **Event querying**: Retrieve events by session or candidate ID

## Tech Stack

### Frontend
- **Next.js 14**: React framework with SSR support
- **TypeScript**: Type-safe development
- **Browser APIs**: Page Visibility API, Clipboard API, Event Listeners
- **WebSocket**: Real-time bidirectional communication

### Backend
- **FastAPI**: High-performance async Python web framework
- **WebSocket**: Real-time event reception
- **MongoDB**: Event storage with indexing
- **Motor**: Async MongoDB driver for Python
- **Pydantic**: Data validation and settings management

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser (Client)                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Tab Visibility Monitor                                  │ │
│  │  • visibilitychange events                              │ │
│  │  • window.blur / window.focus                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Clipboard Monitor                                       │ │
│  │  • copy / paste / cut events                            │ │
│  │  • Optional paste blocking                              │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Inactivity Tracker                                      │ │
│  │  • keydown / keyup events                               │ │
│  │  • mousemove / click events                             │ │
│  │  • Configurable threshold (30s default)                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           ↓ Events                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Event Emitter (Central Hub)                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  WebSocket Client                                        │ │
│  │  • Auto-reconnection with exponential backoff           │ │
│  │  • Message queue for offline events                     │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                             │ WebSocket
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  WebSocket Handler                                       │ │
│  │  • Accepts connections                                   │ │
│  │  • Validates events                                      │ │
│  │  • Adds server timestamps                               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Event Processor                                         │ │
│  │  • Parses event data                                     │ │
│  │  • Creates MonitoringEventDocument                       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  MongoDB Storage                                         │ │
│  │  • Indexed by session_id, candidate_id, timestamp       │ │
│  │  • Optimized for fast retrieval                         │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- MongoDB 7.0+
- Docker & Docker Compose (optional, for containerized setup)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd exam-monitoring

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Backend Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MONGODB_URL="mongodb://localhost:27017"
export DATABASE_NAME="exam_monitoring"

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws" > .env.local

# Run development server
npm run dev

# Access at http://localhost:3000
```

#### MongoDB Setup

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Or install locally
# Follow instructions at: https://www.mongodb.com/docs/manual/installation/
```

## Usage

### Basic Integration

```typescript
import { ActivityMonitor } from '@/components/monitoring/ActivityMonitor';
import { MonitoringConfig } from '@/types/monitoring';

const ExamPage = () => {
  const config: MonitoringConfig = {
    sessionId: 'session-123',
    candidateId: 'candidate-456',
    inactivityThreshold: 30000, // 30 seconds in milliseconds
    disablePaste: true, // Block paste functionality
    websocketUrl: 'ws://localhost:8000/ws',
  };

  return (
    <div>
      <ActivityMonitor config={config} enabled={true} />
      {/* Your exam content here */}
    </div>
  );
};
```

### Consent Banner

```typescript
import { ConsentBanner } from '@/components/ConsentBanner';

const [consentGiven, setConsentGiven] = useState(false);

<ConsentBanner
  onAccept={() => setConsentGiven(true)}
  onDecline={() => alert('Consent required')}
  disablePaste={true}
/>
```

### Retrieving Events

```bash
# Get events by session
curl http://localhost:8000/api/events/session/session-123

# Get events by candidate
curl http://localhost:8000/api/events/candidate/candidate-456
```

## Event Types

### TAB_SWITCHED
```json
{
  "type": "TAB_SWITCHED",
  "timestamp": 1703001234567,
  "inactive_duration": 5000,
  "sessionId": "session-123",
  "candidateId": "candidate-456"
}
```

### COPY_DETECTED
```json
{
  "type": "COPY_DETECTED",
  "timestamp": 1703001234567,
  "content_length": 150,
  "sessionId": "session-123",
  "candidateId": "candidate-456"
}
```

### PASTE_DETECTED
```json
{
  "type": "PASTE_DETECTED",
  "timestamp": 1703001234567,
  "content_length": 200,
  "sessionId": "session-123",
  "candidateId": "candidate-456"
}
```

### KEYBOARD_INACTIVITY
```json
{
  "type": "KEYBOARD_INACTIVITY",
  "timestamp": 1703001234567,
  "duration_seconds": 45,
  "sessionId": "session-123",
  "candidateId": "candidate-456"
}
```

### MOUSE_INACTIVITY
```json
{
  "type": "MOUSE_INACTIVITY",
  "timestamp": 1703001234567,
  "duration_seconds": 30,
  "sessionId": "session-123",
  "candidateId": "candidate-456"
}
```

### ACTIVITY_RESUMED
```json
{
  "type": "ACTIVITY_RESUMED",
  "timestamp": 1703001234567,
  "sessionId": "session-123",
  "candidateId": "candidate-456"
}
```

## Testing

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Watch mode
npm run test:watch
```

### Backend Tests

```bash
cd backend

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Coverage threshold is set to 80%
```

## Browser Compatibility

| Browser | Tab Switching | Copy/Paste | Inactivity | WebSocket |
|---------|--------------|------------|------------|-----------|
| Chrome 90+ | ✅ | ✅ | ✅ | ✅ |
| Firefox 88+ | ✅ | ✅ | ✅ | ✅ |
| Safari 14+ | ✅ | ✅ | ✅ | ✅ |
| Edge 90+ | ✅ | ✅ | ✅ | ✅ |

## Privacy & Compliance

### What We Track
- Event occurrence (tab switches, copy/paste actions, inactivity)
- Timestamps (client and server)
- Content length in bytes (for copy/paste, NOT the actual content)
- Session and candidate identifiers

### What We DON'T Track
- ❌ Actual clipboard content
- ❌ Keystroke data (keylogging)
- ❌ Screenshots or screen recordings
- ❌ Browser history
- ❌ Personal information beyond candidate ID

### Consent Requirements
- Candidates MUST provide explicit consent before monitoring begins
- Consent banner explains all monitoring activities
- Declining consent prevents exam access
- Paste blocking is clearly communicated

### GDPR & Data Protection
- Events are stored with minimal data
- Retention policies can be configured
- Data can be exported or deleted per candidate
- No PII is captured in monitoring events

## Configuration

### Frontend Environment Variables

```env
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### Backend Environment Variables

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=exam_monitoring
COLLECTION_NAME=monitoring_events
CORS_ORIGINS=["http://localhost:3000"]
WEBSOCKET_HEARTBEAT_INTERVAL=30
```

## Performance Considerations

### Frontend
- Event emitter uses efficient observer pattern
- Debounced mousemove events to reduce overhead
- WebSocket reconnection with exponential backoff
- Minimal DOM manipulation

### Backend
- Async/await throughout for non-blocking I/O
- MongoDB indexes on frequently queried fields
- Connection pooling with Motor
- WebSocket connection management

### Database Indexes

```javascript
// Automatically created on startup
db.monitoring_events.createIndex({ "session_id": 1, "timestamp": -1 })
db.monitoring_events.createIndex({ "candidate_id": 1 })
db.monitoring_events.createIndex({ "event_type": 1 })
db.monitoring_events.createIndex({ "received_at": 1 })
```

## Security Considerations

### WebSocket Security
- Origin validation via CORS
- Session-based connection management
- Heartbeat mechanism for connection health

### Data Security
- No sensitive data in events
- Server-side timestamp validation
- Event type validation
- Rate limiting can be added

### Paste Blocking
- Optional per exam configuration
- Cannot be bypassed by developer tools (event interception)
- Clear communication to candidates

## Troubleshooting

### WebSocket Connection Issues

```bash
# Check WebSocket is accessible
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Host: localhost:8000" \
  -H "Origin: http://localhost:3000" \
  http://localhost:8000/ws
```

### MongoDB Connection Issues

```bash
# Test MongoDB connection
mongosh mongodb://localhost:27017

# Check database
use exam_monitoring
db.monitoring_events.find().limit(5)
```

### Frontend Build Issues

```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Roadmap

- [ ] Camera-based proctoring integration
- [ ] Screen recording capabilities
- [ ] AI-based anomaly detection
- [ ] Risk scoring algorithm
- [ ] Admin dashboard for real-time monitoring
- [ ] Mobile browser support improvements
- [ ] Multi-language support

## Acknowledgments

- Page Visibility API: https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API
- Clipboard API: https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API
- FastAPI: https://fastapi.tiangolo.com/
- Next.js: https://nextjs.org/
