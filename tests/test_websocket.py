import pytest
from app.websocket.manager import ConnectionManager
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def connection_manager():
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


@pytest.mark.asyncio
class TestConnectionManager:
    async def test_connect_websocket(self, connection_manager, mock_websocket):
        exam_id = "exam_123"
        await connection_manager.connect(mock_websocket, exam_id)
        
        assert exam_id in connection_manager.active_connections
        assert mock_websocket in connection_manager.active_connections[exam_id]
        mock_websocket.accept.assert_called_once()
    
    async def test_disconnect_websocket(self, connection_manager, mock_websocket):
        exam_id = "exam_123"
        await connection_manager.connect(mock_websocket, exam_id)
        connection_manager.disconnect(mock_websocket, exam_id)
        
        assert mock_websocket not in connection_manager.active_connections.get(exam_id, set())
    
    async def test_disconnect_removes_empty_exam(self, connection_manager, mock_websocket):
        exam_id = "exam_123"
        await connection_manager.connect(mock_websocket, exam_id)
        connection_manager.disconnect(mock_websocket, exam_id)
        
        assert exam_id not in connection_manager.active_connections
    
    async def test_broadcast_to_multiple_connections(self, connection_manager):
        exam_id = "exam_123"
        ws1 = MagicMock()
        ws1.accept = AsyncMock()
        ws1.send_json = AsyncMock()
        
        ws2 = MagicMock()
        ws2.accept = AsyncMock()
        ws2.send_json = AsyncMock()
        
        await connection_manager.connect(ws1, exam_id)
        await connection_manager.connect(ws2, exam_id)
        
        risk_score = {
            "score": 50.0,
            "risk_level": "Medium",
            "contribution_breakdown": []
        }
        
        await connection_manager.broadcast_risk_score(
            exam_id=exam_id,
            session_id="session_456",
            risk_score=risk_score
        )
        
        ws1.send_json.assert_called_once()
        ws2.send_json.assert_called_once()
    
    async def test_broadcast_includes_alert_level(self, connection_manager, mock_websocket):
        exam_id = "exam_123"
        await connection_manager.connect(mock_websocket, exam_id)
        
        risk_score = {
            "score": 75.0,
            "risk_level": "High",
            "contribution_breakdown": []
        }
        
        await connection_manager.broadcast_risk_score(
            exam_id=exam_id,
            session_id="session_456",
            risk_score=risk_score
        )
        
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["alert_level"] == "red"
        assert call_args["score"] == 75.0
    
    async def test_alert_level_yellow(self, connection_manager):
        alert = connection_manager._get_alert_level(50.0)
        assert alert == "yellow"
    
    async def test_alert_level_green(self, connection_manager):
        alert = connection_manager._get_alert_level(30.0)
        assert alert == "green"
    
    async def test_alert_level_red(self, connection_manager):
        alert = connection_manager._get_alert_level(85.0)
        assert alert == "red"
    
    async def test_broadcast_handles_failed_connections(self, connection_manager):
        exam_id = "exam_123"
        
        working_ws = MagicMock()
        working_ws.accept = AsyncMock()
        working_ws.send_json = AsyncMock()
        
        failing_ws = MagicMock()
        failing_ws.accept = AsyncMock()
        failing_ws.send_json = AsyncMock(side_effect=Exception("Connection failed"))
        
        await connection_manager.connect(working_ws, exam_id)
        await connection_manager.connect(failing_ws, exam_id)
        
        risk_score = {
            "score": 50.0,
            "risk_level": "Medium",
            "contribution_breakdown": []
        }
        
        await connection_manager.broadcast_risk_score(
            exam_id=exam_id,
            session_id="session_456",
            risk_score=risk_score
        )
        
        working_ws.send_json.assert_called_once()
        assert failing_ws not in connection_manager.active_connections.get(exam_id, set())
