# Exam Proctoring Risk Scoring Engine

A rule-based risk scoring system for exam proctoring that provides real-time, explainable risk assessments based on detection events.

## Features

- **Real-time Risk Scoring**: Computes risk scores (0-100) as events are received
- **Explainable AI**: Provides detailed contribution breakdown for each event
- **Time Decay**: Recent events weighted more heavily than older events (5-minute rolling window)
- **WebSocket Broadcasting**: Real-time updates to invigilator dashboards
- **MongoDB Persistence**: Complete audit trail and timeline analysis
- **Alert Thresholds**: Yellow (≥50), Red (≥75) alerts for proactive monitoring

## Risk Scoring Formula

```
risk_score = min(100, Σ(event_weight × event_confidence × time_decay))
```

### Event Weights

| Event Type | Weight | Description |
|------------|--------|-------------|
| MULTIPLE_PERSONS | 30 | Multiple people detected in frame |
| MOBILE_DETECTED | 25 | Mobile phone detected |
| TABLET_DETECTED | 20 | Tablet device detected |
| FACE_NOT_DETECTED | 20 | Student's face not visible |
| BACKGROUND_SPEECH | 15 | Speech detected in background |
| MULTIPLE_VOICES | 15 | Multiple voices detected |
| TAB_SWITCHED | 10 | Browser tab switch detected |
| COPY_DETECTED | 5 | Copy action detected |
| PASTE_DETECTED | 5 | Paste action detected |
| KEYBOARD_INACTIVITY | 2 | Extended keyboard inactivity |

### Time Decay

Events decay exponentially over a 5-minute window:

```
decay = exp(-0.5 × (time_elapsed / window_size))
```

- Events at t=0: 100% weight
- Events at t=2.5min: ~78% weight
- Events at t=5min: ~61% weight
- Events >5min: 0% weight

### Risk Levels

| Score Range | Risk Level | Description |
|-------------|-----------|-------------|
| 0-30 | Low | Normal behavior |
| 31-60 | Medium | Some suspicious activity |
| 61-85 | High | Significant concern |
| 86-100 | Critical | Immediate attention required |

## API Endpoints

### Receive Detection Event
```http
POST /exams/{exam_id}/events
Content-Type: application/json

{
  "exam_id": "exam_123",
  "session_id": "session_456",
  "event_type": "MOBILE_DETECTED",
  "confidence": 0.95,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Manually Trigger Risk Computation
```http
POST /exams/{exam_id}/compute-risk?session_id=session_456
```

### Get Current Risk Score
```http
GET /exams/{exam_id}/sessions/{session_id}/risk-score
```

Response:
```json
{
  "exam_id": "exam_123",
  "session_id": "session_456",
  "current_score": 33.75,
  "risk_level": "Medium",
  "last_updated": "2024-01-15T10:30:00Z",
  "contribution_breakdown": [
    {
      "event": "MOBILE_DETECTED",
      "confidence": 0.95,
      "weight": 25,
      "contribution": 23.75,
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "event": "TAB_SWITCHED",
      "confidence": 1.0,
      "weight": 10,
      "contribution": 10.0,
      "timestamp": "2024-01-15T10:29:30Z"
    }
  ]
}
```

### Get Risk Timeline
```http
GET /exams/{exam_id}/sessions/{session_id}/risk-timeline?limit=100
```

### Get Score Breakdown
```http
GET /exams/{exam_id}/sessions/{session_id}/score-breakdown
```

### WebSocket Connection
```
WS /exams/{exam_id}/ws
```

WebSocket message format:
```json
{
  "type": "risk_score_update",
  "exam_id": "exam_123",
  "session_id": "session_456",
  "score": 45.5,
  "risk_level": "Medium",
  "alert_level": "yellow",
  "contribution_breakdown": [...],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Installation

### Prerequisites
- Python 3.9+
- MongoDB 4.4+

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your MongoDB connection details
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

The test suite includes:
- Unit tests for risk scoring engine
- Time decay calculation tests
- Event weight verification
- API endpoint tests
- WebSocket connection tests
- MongoDB integration tests
- Edge case scenarios

## Example Scenarios

### Scenario 1: Phone Detection
**Event:** MOBILE_DETECTED with 95% confidence

**Calculation:**
```
contribution = 0.95 × 25 × 1.0 = 23.75
risk_score = 23.75 (Low risk)
```

### Scenario 2: Multiple Violations
**Events:**
- MOBILE_DETECTED (conf: 0.95, t=0min)
- TAB_SWITCHED (conf: 1.0, t=0min)
- FACE_NOT_DETECTED (conf: 0.85, t=1min)

**Calculation:**
```
mobile: 0.95 × 25 × 1.0 = 23.75
tab: 1.0 × 10 × 1.0 = 10.0
face: 0.85 × 20 × 0.90 = 15.3 (with decay)
risk_score = 49.05 (Medium risk)
```

### Scenario 3: Time Decay Effect
**Event:** MOBILE_DETECTED (conf: 1.0)

| Time Elapsed | Decay Factor | Contribution | Total Score |
|--------------|-------------|--------------|-------------|
| 0 min | 1.0 | 25.0 | 25.0 |
| 2.5 min | 0.78 | 19.5 | 19.5 |
| 5 min | 0.61 | 15.25 | 15.25 |
| 6 min | 0.0 | 0.0 | 0.0 |

## Configuration

Event weights can be configured via environment variables:

```env
WEIGHT_MULTIPLE_PERSONS=30
WEIGHT_MOBILE_DETECTED=25
WEIGHT_BACKGROUND_SPEECH=15
WEIGHT_TAB_SWITCHED=10
WEIGHT_FACE_NOT_DETECTED=20
WEIGHT_COPY_DETECTED=5
WEIGHT_PASTE_DETECTED=5
WEIGHT_KEYBOARD_INACTIVITY=2
WEIGHT_TABLET_DETECTED=20
WEIGHT_MULTIPLE_VOICES=15

RISK_SCORE_WINDOW_MINUTES=5
TIME_DECAY_FACTOR=0.5
```

## Architecture

```
┌─────────────────┐
│  Detection ML   │
│     Models      │
└────────┬────────┘
         │ events
         ▼
┌─────────────────┐     ┌──────────────┐
│   FastAPI API   │────▶│   MongoDB    │
│   (risk_scoring)│     │  (history)   │
└────────┬────────┘     └──────────────┘
         │ websocket
         ▼
┌─────────────────┐
│  Invigilator    │
│   Dashboard     │
└─────────────────┘
```

## MongoDB Collections

### detection_events
```json
{
  "_id": ObjectId,
  "exam_id": "exam_123",
  "session_id": "session_456",
  "event_type": "MOBILE_DETECTED",
  "confidence": 0.95,
  "timestamp": ISODate("2024-01-15T10:30:00Z"),
  "metadata": {}
}
```

### risk_score_history
```json
{
  "_id": ObjectId,
  "exam_id": "exam_123",
  "session_id": "session_456",
  "score": 45.5,
  "risk_level": "Medium",
  "timestamp": ISODate("2024-01-15T10:30:00Z"),
  "contribution_breakdown": [
    {
      "event": "MOBILE_DETECTED",
      "confidence": 0.95,
      "weight": 25,
      "contribution": 23.75,
      "timestamp": ISODate("2024-01-15T10:30:00Z")
    }
  ]
}
```

## Future Enhancements (Phase 2)

- Admin dashboard for weight configuration
- Custom event weight profiles per exam
- Machine learning-based weight optimization
- Historical pattern analysis
- Batch processing for post-exam analysis

## License

[Your License Here]

## Support

For issues and questions, please contact [support contact].
