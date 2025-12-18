import pytest
import asyncio
import json
import base64
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

from app.models.alerts import (
    AlertEvent, AlertSeverity, AlertType, EvidenceSnapshot,
    AlertAcknowledgmentRequest, AlertQueryRequest
)
from app.services.alert_service import AlertService
from app.services.websocket_manager import WebSocketManager
from app.services.evidence_service import EvidenceSnapshotService


@pytest.fixture
async def alert_service():
    """Create alert service instance for testing"""
    service = AlertService()
    yield service


@pytest.fixture
def mock_websocket():
    """Create mock WebSocket for testing"""
    websocket = Mock()
    websocket.send_text = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.receive_text = AsyncMock()
    websocket.close = AsyncMock()
    return websocket


@pytest.fixture
def websocket_manager():
    """Create WebSocket manager instance for testing"""
    return WebSocketManager()


@pytest.fixture
def evidence_service():
    """Create evidence service instance for testing"""
    return EvidenceSnapshotService()


class TestAlertModels:
    """Test alert data models"""
    
    def test_alert_event_creation(self):
        """Test AlertEvent model creation"""
        alert = AlertEvent(
            exam_id="exam_123",
            session_id="session_456",
            event_type=AlertType.MOBILE_DETECTED,
            severity=AlertSeverity.CRITICAL,
            confidence=0.95,
            risk_score_delta=25,
            current_risk_score=50,
            message="Mobile phone detected in camera frame"
        )
        
        assert alert.exam_id == "exam_123"
        assert alert.session_id == "session_456"
        assert alert.event_type == AlertType.MOBILE_DETECTED
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.confidence == 0.95
        assert alert.risk_score_delta == 25
        assert alert.current_risk_score == 50
        assert alert.message == "Mobile phone detected in camera frame"
        assert alert.acknowledged is False
        assert alert.alert_id is not None
    
    def test_evidence_snapshot_creation(self):
        """Test EvidenceSnapshot model creation"""
        snapshot = EvidenceSnapshot(
            exam_id="exam_123",
            session_id="session_456",
            alert_id="alert_789",
            event_type=AlertType.MULTIPLE_FACES,
            frame_number=42,
            risk_score=70,
            file_path="/path/to/snapshot.jpg",
            file_size=1024,
            retention_expires_at=datetime.utcnow()
        )
        
        assert snapshot.exam_id == "exam_123"
        assert snapshot.session_id == "session_456"
        assert snapshot.alert_id == "alert_789"
        assert snapshot.event_type == AlertType.MULTIPLE_FACES
        assert snapshot.frame_number == 42
        assert snapshot.risk_score == 70
        assert snapshot.file_path == "/path/to/snapshot.jpg"
        assert snapshot.file_size == 1024
        assert snapshot.snapshot_id is not None
    
    def test_alert_severity_enum(self):
        """Test AlertSeverity enum values"""
        assert AlertSeverity.INFO == "INFO"
        assert AlertSeverity.WARNING == "WARNING"
        assert AlertSeverity.CRITICAL == "CRITICAL"
        assert AlertSeverity.EMERGENCY == "EMERGENCY"
    
    def test_alert_type_enum(self):
        """Test AlertType enum values"""
        assert AlertType.MOBILE_DETECTED == "MOBILE_DETECTED"
        assert AlertType.MULTIPLE_FACES == "MULTIPLE_FACES"
        assert AlertType.TAB_SWITCH == "TAB_SWITCH"
        assert AlertType.LIVENESS_CONFIRMED == "LIVENESS_CONFIRMED"


class TestAlertService:
    """Test AlertService functionality"""
    
    @pytest.mark.asyncio
    async def test_generate_critical_alert(self, alert_service):
        """Test generating a critical alert"""
        with patch.object(alert_service, '_store_alert', return_value=True), \
             patch.object(alert_service, '_calculate_risk_score', return_value=30), \
             patch.object(alert_service, '_update_risk_score_cache', return_value=None), \
             patch('app.services.alert_service.websocket_manager') as mock_ws_manager:
            
            mock_ws_manager.broadcast_alert = AsyncMock()
            
            alert = await alert_service.generate_alert(
                exam_id="exam_123",
                session_id="session_456",
                event_type=AlertType.MOBILE_DETECTED,
                confidence=0.95
            )
            
            assert alert is not None
            assert alert.exam_id == "exam_123"
            assert alert.session_id == "session_456"
            assert alert.event_type == AlertType.MOBILE_DETECTED
            assert alert.severity == AlertSeverity.CRITICAL
            assert alert.confidence == 0.95
            assert alert.risk_score_delta == 25
            assert alert.current_risk_score == 55  # 30 + 25
            assert "Mobile phone detected" in alert.message
            
            mock_ws_manager.broadcast_alert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_warning_alert(self, alert_service):
        """Test generating a warning alert"""
        with patch.object(alert_service, '_store_alert', return_value=True), \
             patch.object(alert_service, '_calculate_risk_score', return_value=20), \
             patch.object(alert_service, '_update_risk_score_cache', return_value=None), \
             patch('app.services.alert_service.websocket_manager') as mock_ws_manager:
            
            mock_ws_manager.broadcast_alert = AsyncMock()
            
            alert = await alert_service.generate_alert(
                exam_id="exam_123",
                session_id="session_456",
                event_type=AlertType.TAB_SWITCH,
                confidence=0.9
            )
            
            assert alert is not None
            assert alert.severity == AlertSeverity.WARNING
            assert alert.risk_score_delta == 10
            assert alert.current_risk_score == 30  # 20 + 10
    
    @pytest.mark.asyncio
    async def test_generate_info_alert(self, alert_service):
        """Test generating an info alert"""
        with patch.object(alert_service, '_store_alert', return_value=True), \
             patch.object(alert_service, '_calculate_risk_score', return_value=50), \
             patch.object(alert_service, '_update_risk_score_cache', return_value=None), \
             patch('app.services.alert_service.websocket_manager') as mock_ws_manager:
            
            mock_ws_manager.broadcast_alert = AsyncMock()
            
            alert = await alert_service.generate_alert(
                exam_id="exam_123",
                session_id="session_456",
                event_type=AlertType.LIVENESS_CONFIRMED,
                confidence=0.85
            )
            
            assert alert is not None
            assert alert.severity == AlertSeverity.INFO
            assert alert.risk_score_delta == -5
            assert alert.current_risk_score == 45  # 50 - 5
            assert "Liveness verification successful" in alert.message
    
    @pytest.mark.asyncio
    async def test_alert_below_confidence_threshold(self, alert_service):
        """Test that alerts below confidence threshold are not generated"""
        with patch.object(alert_service, '_store_alert', return_value=True), \
             patch.object(alert_service, '_calculate_risk_score', return_value=20), \
             patch('app.services.alert_service.websocket_manager') as mock_ws_manager:
            
            mock_ws_manager.broadcast_alert = AsyncMock()
            
            # Mobile detection requires 0.8 confidence, but we pass 0.5
            alert = await alert_service.generate_alert(
                exam_id="exam_123",
                session_id="session_456",
                event_type=AlertType.MOBILE_DETECTED,
                confidence=0.5
            )
            
            assert alert is None
            mock_ws_manager.broadcast_alert.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, alert_service):
        """Test acknowledging an alert"""
        with patch.object(alert_service.mongodb.alerts, 'update_one', return_value=Mock(modified_count=1)):
            result = await alert_service.acknowledge_alert("alert_123", "invigilator_456")
            assert result is True
    
    @pytest.mark.asyncio
    async def test_get_alert_by_id(self, alert_service):
        """Test getting alert by ID"""
        mock_alert_data = {
            "alert_id": "alert_123",
            "exam_id": "exam_456",
            "session_id": "session_789",
            "event_type": AlertType.MOBILE_DETECTED,
            "severity": AlertSeverity.CRITICAL,
            "confidence": 0.95,
            "risk_score_delta": 25,
            "current_risk_score": 50,
            "message": "Mobile phone detected",
            "timestamp": datetime.utcnow()
        }
        
        with patch.object(alert_service.mongodb.alerts, 'find_one', return_value=mock_alert_data):
            alert = await alert_service.get_alert_by_id("alert_123")
            assert alert is not None
            assert alert.alert_id == "alert_123"
            assert alert.exam_id == "exam_456"
    
    @pytest.mark.asyncio
    async def test_start_exam_monitoring(self, alert_service):
        """Test starting exam monitoring"""
        with patch.object(alert_service, 'generate_alert', return_value=Mock()):
            result = await alert_service.start_exam_monitoring("exam_123", "session_456")
            assert result is True
            assert "exam_123" in alert_service.risk_score_cache
    
    @pytest.mark.asyncio
    async def test_end_exam_monitoring(self, alert_service):
        """Test ending exam monitoring"""
        # Set up cache
        alert_service.risk_score_cache["exam_123"] = 45
        
        with patch.object(alert_service, 'generate_alert', return_value=Mock()):
            result = await alert_service.end_exam_monitoring("exam_123", "session_456")
            assert result is True
            assert "exam_123" not in alert_service.risk_score_cache


class TestWebSocketManager:
    """Test WebSocket connection management"""
    
    @pytest.mark.asyncio
    async def test_connect_new_websocket(self, websocket_manager, mock_websocket):
        """Test connecting a new WebSocket"""
        connection_id = await websocket_manager.connect(
            mock_websocket, "exam_123", "invigilator_456"
        )
        
        assert connection_id is not None
        assert "invigilator_456" in connection_id
        assert "exam_123" in websocket_manager.active_connections
        assert mock_websocket in websocket_manager.active_connections["exam_123"]
        assert mock_websocket.send_text.called
    
    @pytest.mark.asyncio
    async def test_disconnect_websocket(self, websocket_manager, mock_websocket):
        """Test disconnecting a WebSocket"""
        # First connect
        await websocket_manager.connect(mock_websocket, "exam_123", "invigilator_456")
        assert mock_websocket in websocket_manager.active_connections["exam_123"]
        
        # Then disconnect
        websocket_manager.disconnect(mock_websocket)
        
        assert "exam_123" not in websocket_manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_alert(self, websocket_manager, mock_websocket):
        """Test broadcasting an alert to connected invigilators"""
        # Connect first
        await websocket_manager.connect(mock_websocket, "exam_123", "invigilator_456")
        
        # Create test alert
        alert = AlertEvent(
            exam_id="exam_123",
            session_id="session_456",
            event_type=AlertType.MOBILE_DETECTED,
            severity=AlertSeverity.CRITICAL,
            confidence=0.95,
            risk_score_delta=25,
            current_risk_score=50,
            message="Mobile phone detected"
        )
        
        # Broadcast alert
        await websocket_manager.broadcast_alert("exam_123", alert)
        
        # Check that alert was sent
        assert mock_websocket.send_text.called
        sent_message = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_message["type"] == "alert"
        assert sent_message["alert"]["event_type"] == AlertType.MOBILE_DETECTED
    
    @pytest.mark.asyncio
    async def test_multiple_invigilators(self, websocket_manager):
        """Test multiple invigilators receiving the same alert"""
        # Create multiple mock websockets
        websocket1 = Mock()
        websocket1.send_text = AsyncMock()
        websocket1.accept = AsyncMock()
        
        websocket2 = Mock()
        websocket2.send_text = AsyncMock()
        websocket2.accept = AsyncMock()
        
        # Connect both
        await websocket_manager.connect(websocket1, "exam_123", "invigilator_1")
        await websocket_manager.connect(websocket2, "exam_123", "invigilator_2")
        
        # Create and broadcast alert
        alert = AlertEvent(
            exam_id="exam_123",
            session_id="session_456",
            event_type=AlertType.MULTIPLE_FACES,
            severity=AlertSeverity.CRITICAL,
            confidence=0.95,
            risk_score_delta=20,
            current_risk_score=70,
            message="Multiple faces detected"
        )
        
        await websocket_manager.broadcast_alert("exam_123", alert)
        
        # Both websockets should have received the alert
        assert websocket1.send_text.called
        assert websocket2.send_text.called
    
    @pytest.mark.asyncio
    async def test_get_connected_invigilators(self, websocket_manager, mock_websocket):
        """Test getting list of connected invigilators"""
        await websocket_manager.connect(mock_websocket, "exam_123", "invigilator_456")
        
        invigilators = websocket_manager.get_connected_invigilators("exam_123")
        assert len(invigilators) == 1
        assert invigilators[0].invigilator_id == "invigilator_456"
        assert invigilators[0].exam_id == "exam_123"
    
    @pytest.mark.asyncio
    async def test_connection_count(self, websocket_manager, mock_websocket):
        """Test getting connection count for an exam"""
        assert websocket_manager.get_connection_count("exam_123") == 0
        
        await websocket_manager.connect(mock_websocket, "exam_123", "invigilator_456")
        assert websocket_manager.get_connection_count("exam_123") == 1


class TestEvidenceService:
    """Test evidence snapshot service"""
    
    @pytest.mark.asyncio
    async def test_capture_snapshot_with_frame_data(self, evidence_service):
        """Test capturing a snapshot with frame data"""
        # Create mock frame data (base64 encoded)
        frame_data = base64.b64encode(b"fake_image_data").decode()
        
        with patch.object(evidence_service, '_encrypt_data', return_value=b"encrypted_data"), \
             patch.object(evidence_service, 'minio_client', return_value=None):  # Use local storage
            
            snapshot = await evidence_service.capture_snapshot(
                frame_data=frame_data,
                exam_id="exam_123",
                session_id="session_456",
                alert_id="alert_789",
                event_type=AlertType.MULTIPLE_FACES,
                frame_number=42,
                risk_score=70
            )
            
            assert snapshot is not None
            assert snapshot.exam_id == "exam_123"
            assert snapshot.session_id == "session_456"
            assert snapshot.alert_id == "alert_789"
            assert snapshot.event_type == AlertType.MULTIPLE_FACES
            assert snapshot.frame_number == 42
            assert snapshot.risk_score == 70
            assert snapshot.file_size > 0
    
    @pytest.mark.asyncio
    async def test_encryption_decryption(self, evidence_service):
        """Test data encryption and decryption"""
        test_data = b"test evidence data"
        
        # Encrypt the data
        encrypted = evidence_service._encrypt_data(test_data)
        assert encrypted is not None
        assert encrypted != test_data
        
        # Decrypt the data
        decrypted = evidence_service._decrypt_data(encrypted)
        assert decrypted is not None
        assert decrypted == test_data
    
    def test_set_retention_period(self, evidence_service):
        """Test setting snapshot retention period"""
        evidence_service.set_retention_period(60)
        assert evidence_service.snapshot_retention_days == 60
        
        # Test invalid retention period
        evidence_service.set_retention_period(500)  # Should be ignored
        assert evidence_service.snapshot_retention_days == 60


class TestAlertPayloadValidation:
    """Test alert payload format and validation"""
    
    def test_alert_payload_format(self):
        """Test that alert payload matches required format"""
        alert = AlertEvent(
            exam_id="exam_123",
            session_id="session_456",
            event_type=AlertType.MOBILE_DETECTED,
            severity=AlertSeverity.CRITICAL,
            confidence=0.95,
            risk_score_delta=25,
            current_risk_score=50,
            message="Mobile phone detected in camera frame",
            evidence_snapshot_id="snapshot_789"
        )
        
        # Convert to dict and verify all required fields
        alert_dict = alert.dict()
        
        required_fields = [
            "alert_id", "exam_id", "session_id", "timestamp", 
            "event_type", "severity", "confidence", "risk_score_delta",
            "current_risk_score", "message", "evidence_snapshot_id"
        ]
        
        for field in required_fields:
            assert field in alert_dict
        
        # Verify field types and values
        assert isinstance(alert_dict["alert_id"], str)
        assert isinstance(alert_dict["exam_id"], str)
        assert isinstance(alert_dict["session_id"], str)
        assert isinstance(alert_dict["timestamp"], datetime)
        assert alert_dict["event_type"] == AlertType.MOBILE_DETECTED
        assert alert_dict["severity"] == AlertSeverity.CRITICAL
        assert isinstance(alert_dict["confidence"], float)
        assert 0.0 <= alert_dict["confidence"] <= 1.0
        assert isinstance(alert_dict["risk_score_delta"], int)
        assert isinstance(alert_dict["current_risk_score"], int)
        assert isinstance(alert_dict["message"], str)
        assert isinstance(alert_dict["evidence_snapshot_id"], str)
    
    def test_confidence_range_validation(self):
        """Test confidence score validation"""
        # Valid confidence
        alert = AlertEvent(
            exam_id="exam_123",
            session_id="session_456",
            event_type=AlertType.MOBILE_DETECTED,
            severity=AlertSeverity.CRITICAL,
            confidence=0.95,
            risk_score_delta=25,
            current_risk_score=50,
            message="Mobile phone detected"
        )
        assert alert.confidence == 0.95
        
        # Test invalid confidence (too high)
        with pytest.raises(ValueError):
            AlertEvent(
                exam_id="exam_123",
                session_id="session_456",
                event_type=AlertType.MOBILE_DETECTED,
                severity=AlertSeverity.CRITICAL,
                confidence=1.5,  # Invalid: > 1.0
                risk_score_delta=25,
                current_risk_score=50,
                message="Mobile phone detected"
            )
    
    def test_risk_score_validation(self):
        """Test risk score range validation"""
        # Valid risk scores
        alert = AlertEvent(
            exam_id="exam_123",
            session_id="session_456",
            event_type=AlertType.MOBILE_DETECTED,
            severity=AlertSeverity.CRITICAL,
            confidence=0.95,
            risk_score_delta=25,
            current_risk_score=50,  # Valid: 0-100
            message="Mobile phone detected"
        )
        assert alert.current_risk_score == 50
        
        # Test invalid risk score (too high)
        with pytest.raises(ValueError):
            AlertEvent(
                exam_id="exam_123",
                session_id="session_456",
                event_type=AlertType.MOBILE_DETECTED,
                severity=AlertSeverity.CRITICAL,
                confidence=0.95,
                risk_score_delta=25,
                current_risk_score=150,  # Invalid: > 100
                message="Mobile phone detected"
            )


class TestWebSocketMessageProtocol:
    """Test WebSocket message protocol and ordering"""
    
    @pytest.mark.asyncio
    async def test_connection_establishment(self, websocket_manager, mock_websocket):
        """Test WebSocket connection establishment message"""
        await websocket_manager.connect(mock_websocket, "exam_123", "invigilator_456")
        
        # Check that connection establishment message was sent
        assert mock_websocket.send_text.called
        sent_message = json.loads(mock_websocket.send_text.call_args[0][0])
        
        assert sent_message["type"] == "connection_established"
        assert "connection_id" in sent_message
        assert "timestamp" in sent_message
    
    @pytest.mark.asyncio
    async def test_message_ordering(self, websocket_manager, mock_websocket):
        """Test that messages have proper ordering"""
        await websocket_manager.connect(mock_websocket, "exam_123", "invigilator_456")
        
        # Create and send test messages
        alert1 = AlertEvent(
            exam_id="exam_123",
            session_id="session_456",
            event_type=AlertType.LIVENESS_CONFIRMED,
            severity=AlertSeverity.INFO,
            confidence=0.85,
            risk_score_delta=-5,
            current_risk_score=45,
            message="Liveness confirmed"
        )
        
        alert2 = AlertEvent(
            exam_id="exam_123",
            session_id="session_456",
            event_type=AlertType.TAB_SWITCH,
            severity=AlertSeverity.WARNING,
            confidence=0.9,
            risk_score_delta=10,
            current_risk_score=55,
            message="Tab switch detected"
        )
        
        await websocket_manager.broadcast_alert("exam_123", alert1)
        await websocket_manager.broadcast_alert("exam_123", alert2)
        
        # Check that both messages were sent with proper ordering
        assert mock_websocket.send_text.call_count == 3  # 1 connection + 2 alerts
        
        # Verify message structure
        for call in mock_websocket.send_text.call_args_list:
            message = json.loads(call[0][0])
            assert "message_id" in message
            assert "server_timestamp" in message
    
    @pytest.mark.asyncio
    async def test_reconnection_handling(self, websocket_manager):
        """Test reconnection with message resumption"""
        # Create mock WebSocket for reconnection
        old_websocket = Mock()
        old_websocket.send_text = AsyncMock()
        old_websocket.accept = AsyncMock()
        
        new_websocket = Mock()
        new_websocket.send_text = AsyncMock()
        new_websocket.accept = AsyncMock()
        
        # Initial connection
        await websocket_manager.connect(old_websocket, "exam_123", "invigilator_456")
        
        # Simulate reconnection
        await websocket_manager.handle_reconnection(
            new_websocket, "exam_123", "invigilator_456", "msg_10"
        )
        
        # Check that new connection was established
        assert new_websocket.send_text.called
        sent_message = json.loads(new_websocket.send_text.call_args[0][0])
        assert sent_message["type"] == "connection_established"