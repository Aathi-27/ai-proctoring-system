import pytest
from httpx import AsyncClient
from datetime import datetime
from app.main import app
from app.database.mongodb import MongoDB
from app.models.events import EventType


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def setup_api_test_db(test_db):
    MongoDB.database = test_db
    await test_db.detection_events.delete_many({})
    await test_db.risk_score_history.delete_many({})
    yield test_db
    await test_db.detection_events.delete_many({})
    await test_db.risk_score_history.delete_many({})


@pytest.mark.asyncio
class TestHealthEndpoint:
    async def test_root_endpoint(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
    
    async def test_health_check(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
class TestComputeRiskScore:
    async def test_compute_risk_score_no_events(self, client, setup_api_test_db):
        response = await client.post(
            "/exams/exam_123/compute-risk",
            params={"session_id": "session_456"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["exam_id"] == "exam_123"
        assert data["session_id"] == "session_456"
        assert data["score"] == 0.0
        assert data["risk_level"] == "Low"
    
    async def test_compute_risk_score_with_events(self, client, setup_api_test_db):
        event_data = {
            "exam_id": "exam_123",
            "session_id": "session_456",
            "event_type": "MOBILE_DETECTED",
            "confidence": 0.95
        }
        
        await client.post("/exams/exam_123/events", json=event_data)
        
        response = await client.post(
            "/exams/exam_123/compute-risk",
            params={"session_id": "session_456"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["score"] > 0


@pytest.mark.asyncio
class TestReceiveDetectionEvent:
    async def test_receive_valid_event(self, client, setup_api_test_db):
        event_data = {
            "exam_id": "exam_123",
            "session_id": "session_456",
            "event_type": "MOBILE_DETECTED",
            "confidence": 0.95
        }
        
        response = await client.post("/exams/exam_123/events", json=event_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "risk_score" in data
        assert "risk_level" in data
    
    async def test_receive_event_exam_id_mismatch(self, client, setup_api_test_db):
        event_data = {
            "exam_id": "exam_999",
            "session_id": "session_456",
            "event_type": "MOBILE_DETECTED",
            "confidence": 0.95
        }
        
        response = await client.post("/exams/exam_123/events", json=event_data)
        
        assert response.status_code == 400
    
    async def test_receive_event_invalid_confidence(self, client, setup_api_test_db):
        event_data = {
            "exam_id": "exam_123",
            "session_id": "session_456",
            "event_type": "MOBILE_DETECTED",
            "confidence": 1.5
        }
        
        response = await client.post("/exams/exam_123/events", json=event_data)
        
        assert response.status_code == 422


@pytest.mark.asyncio
class TestGetCurrentRiskScore:
    async def test_get_current_risk_score(self, client, setup_api_test_db):
        event_data = {
            "exam_id": "exam_123",
            "session_id": "session_456",
            "event_type": "TAB_SWITCHED",
            "confidence": 1.0
        }
        
        await client.post("/exams/exam_123/events", json=event_data)
        
        response = await client.get("/exams/exam_123/sessions/session_456/risk-score")
        
        assert response.status_code == 200
        data = response.json()
        assert data["exam_id"] == "exam_123"
        assert data["session_id"] == "session_456"
        assert data["current_score"] >= 0
        assert "risk_level" in data
        assert "contribution_breakdown" in data
    
    async def test_get_risk_score_no_events(self, client, setup_api_test_db):
        response = await client.get("/exams/exam_999/sessions/session_999/risk-score")
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_score"] == 0.0


@pytest.mark.asyncio
class TestGetRiskTimeline:
    async def test_get_risk_timeline(self, client, setup_api_test_db):
        for i in range(3):
            event_data = {
                "exam_id": "exam_123",
                "session_id": "session_456",
                "event_type": "TAB_SWITCHED",
                "confidence": 1.0
            }
            await client.post("/exams/exam_123/events", json=event_data)
        
        response = await client.get("/exams/exam_123/sessions/session_456/risk-timeline")
        
        assert response.status_code == 200
        data = response.json()
        assert data["exam_id"] == "exam_123"
        assert data["session_id"] == "session_456"
        assert "timeline" in data
        assert len(data["timeline"]) >= 3
    
    async def test_get_timeline_with_limit(self, client, setup_api_test_db):
        for i in range(5):
            event_data = {
                "exam_id": "exam_123",
                "session_id": "session_456",
                "event_type": "TAB_SWITCHED",
                "confidence": 1.0
            }
            await client.post("/exams/exam_123/events", json=event_data)
        
        response = await client.get(
            "/exams/exam_123/sessions/session_456/risk-timeline",
            params={"limit": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["timeline"]) <= 2


@pytest.mark.asyncio
class TestGetScoreBreakdown:
    async def test_get_score_breakdown(self, client, setup_api_test_db):
        events = [
            {
                "exam_id": "exam_123",
                "session_id": "session_456",
                "event_type": "MOBILE_DETECTED",
                "confidence": 0.95
            },
            {
                "exam_id": "exam_123",
                "session_id": "session_456",
                "event_type": "TAB_SWITCHED",
                "confidence": 1.0
            }
        ]
        
        for event_data in events:
            await client.post("/exams/exam_123/events", json=event_data)
        
        response = await client.get("/exams/exam_123/sessions/session_456/score-breakdown")
        
        assert response.status_code == 200
        data = response.json()
        assert data["exam_id"] == "exam_123"
        assert data["session_id"] == "session_456"
        assert data["current_score"] > 0
        assert data["total_events"] >= 2
        assert "contribution_breakdown" in data
        assert len(data["contribution_breakdown"]) >= 2
    
    async def test_breakdown_shows_contributions(self, client, setup_api_test_db):
        event_data = {
            "exam_id": "exam_123",
            "session_id": "session_456",
            "event_type": "MULTIPLE_PERSONS",
            "confidence": 1.0
        }
        
        await client.post("/exams/exam_123/events", json=event_data)
        
        response = await client.get("/exams/exam_123/sessions/session_456/score-breakdown")
        
        assert response.status_code == 200
        data = response.json()
        contributions = data["contribution_breakdown"]
        
        assert len(contributions) > 0
        first_contribution = contributions[0]
        assert "event" in first_contribution
        assert "confidence" in first_contribution
        assert "weight" in first_contribution
        assert "contribution" in first_contribution
        assert first_contribution["event"] == "MULTIPLE_PERSONS"
        assert first_contribution["weight"] == 30


@pytest.mark.asyncio
class TestEventTypes:
    async def test_all_event_types_accepted(self, client, setup_api_test_db):
        event_types = [
            "MULTIPLE_PERSONS",
            "MOBILE_DETECTED",
            "BACKGROUND_SPEECH",
            "TAB_SWITCHED",
            "FACE_NOT_DETECTED",
            "COPY_DETECTED",
            "PASTE_DETECTED",
            "KEYBOARD_INACTIVITY",
            "TABLET_DETECTED",
            "MULTIPLE_VOICES"
        ]
        
        for event_type in event_types:
            event_data = {
                "exam_id": "exam_123",
                "session_id": f"session_{event_type}",
                "event_type": event_type,
                "confidence": 0.9
            }
            
            response = await client.post("/exams/exam_123/events", json=event_data)
            assert response.status_code == 200, f"Failed for {event_type}"
