import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Exam Monitoring API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_websocket_connection():
    from app.websocket import manager
    from unittest.mock import AsyncMock, MagicMock
    
    websocket = MagicMock()
    websocket.accept = AsyncMock()
    session_id = "test-session"
    
    await manager.connect(websocket, session_id)
    
    assert session_id in manager.active_connections
    assert websocket in manager.active_connections[session_id]
    
    manager.disconnect(websocket, session_id)
    assert session_id not in manager.active_connections


@pytest.mark.asyncio
async def test_handle_monitoring_event():
    from app.websocket import handle_monitoring_event
    from app.models import MonitoringEventType
    
    event_data = {
        "type": MonitoringEventType.TAB_SWITCHED.value,
        "timestamp": 1234567890,
        "sessionId": "test-session",
        "candidateId": "test-candidate",
        "inactive_duration": 5000,
    }
    
    event_doc = await handle_monitoring_event(event_data)
    
    assert event_doc.event_type == "TAB_SWITCHED"
    assert event_doc.timestamp == 1234567890
    assert event_doc.session_id == "test-session"
    assert event_doc.candidate_id == "test-candidate"
    assert event_doc.inactive_duration == 5000


@pytest.mark.asyncio
async def test_handle_clipboard_event():
    from app.websocket import handle_monitoring_event
    from app.models import MonitoringEventType
    
    event_data = {
        "type": MonitoringEventType.COPY_DETECTED.value,
        "timestamp": 1234567890,
        "sessionId": "test-session",
        "candidateId": "test-candidate",
        "content_length": 100,
    }
    
    event_doc = await handle_monitoring_event(event_data)
    
    assert event_doc.event_type == "COPY_DETECTED"
    assert event_doc.content_length == 100


@pytest.mark.asyncio
async def test_handle_inactivity_event():
    from app.websocket import handle_monitoring_event
    from app.models import MonitoringEventType
    
    event_data = {
        "type": MonitoringEventType.KEYBOARD_INACTIVITY.value,
        "timestamp": 1234567890,
        "sessionId": "test-session",
        "candidateId": "test-candidate",
        "duration_seconds": 30,
    }
    
    event_doc = await handle_monitoring_event(event_data)
    
    assert event_doc.event_type == "KEYBOARD_INACTIVITY"
    assert event_doc.duration_seconds == 30
