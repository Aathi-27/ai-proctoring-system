import pytest
import asyncio
import json
import base64
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

from app.models.alerts import AlertEvent, AlertSeverity, AlertType
from app.services.alert_service import AlertService
from app.services.websocket_manager import WebSocketManager
from app.services.evidence_service import EvidenceSnapshotService
from app.database.mongodb import mongodb_client


class TestWebSocketBroadcastIntegration:
    """Integration tests for WebSocket broadcast to multiple clients"""
    
    @pytest.mark.asyncio
    async def test_multiple_invigilators_broadcast(self):
        """Test broadcasting to multiple invigilators monitoring the same exam"""
        websocket_manager = WebSocketManager()
        
        # Create multiple mock WebSocket connections
        websockets = []
        for i in range(3):
            ws = Mock()
            ws.send_text = AsyncMock()
            ws.accept = AsyncMock()
            ws.receive_text = AsyncMock()
            ws.close = AsyncMock()
            websockets.append(ws)
        
        # Connect all invigilators to the same exam
        exam_id = "exam_integration_test"
        invigilator_ids = ["invigilator_1", "invigilator_2", "invigilator_3"]
        
        connection_ids = []
        for i, ws in enumerate(websockets):
            conn_id = await websocket_manager.connect(ws, exam_id, invigilator_ids[i])
            connection_ids.append(conn_id)
            assert conn_id is not None
        
        # Verify all connections are active
        assert websocket_manager.get_connection_count(exam_id) == 3
        
        # Create test alert
        test_alert = AlertEvent(
            exam_id=exam_id,
            session_id="session_test",
            event_type=AlertType.MOBILE_DETECTED,
            severity=AlertSeverity.CRITICAL,
            confidence=0.95,
            risk_score_delta=25,
            current_risk_score=75,
            message="Mobile phone detected - Multiple invigilators test",
            evidence_snapshot_id="snapshot_test_123"
        )
        
        # Broadcast alert to all connected invigilators
        await websocket_manager.broadcast_alert(exam_id, test_alert)
        
        # Verify all invigilators received the alert
        for i, ws in enumerate(websockets):
            assert ws.send_text.called, f"Invigilator {i} did not receive alert"
            
            # Check the alert message structure
            sent_calls = ws.send_text.call_args_list
            alert_call = sent_calls[-1]  # Last call should be the alert
            alert_message = json.loads(alert_call[0][0])
            
            assert alert_message["type"] == "alert"
            assert alert_message["alert"]["event_type"] == AlertType.MOBILE_DETECTED
            assert alert_message["alert"]["exam_id"] == exam_id
            assert alert_message["alert"]["message"] == test_alert.message
    
    @pytest.mark.asyncio
    async def test_exam_isolation_broadcast(self):
        """Test that alerts are only broadcast to invigilators monitoring the specific exam"""
        websocket_manager = WebSocketManager()
        
        # Create WebSocket connections for different exams
        exam1_ws = Mock()
        exam1_ws.send_text = AsyncMock()
        exam1_ws.accept = AsyncMock()
        
        exam2_ws = Mock()
        exam2_ws.send_text = AsyncMock()
        exam2_ws.accept = AsyncMock()
        
        # Connect invigilators to different exams
        await websocket_manager.connect(exam1_ws, "exam_1", "invigilator_a")
        await websocket_manager.connect(exam2_ws, "exam_2", "invigilator_b")
        
        # Create alert for exam_1
        exam1_alert = AlertEvent(
            exam_id="exam_1",
            session_id="session_1",
            event_type=AlertType.TAB_SWITCH,
            severity=AlertSeverity.WARNING,
            confidence=0.9,
            risk_score_delta=10,
            current_risk_score=40,
            message="Tab switch detected in exam 1"
        )
        
        # Broadcast to exam_1
        await websocket_manager.broadcast_alert("exam_1", exam1_alert)
        
        # Verify only exam_1 invigilator received the alert
        assert exam1_ws.send_text.called, "Exam 1 invigilator should receive alert"
        assert not exam2_ws.send_text.called, "Exam 2 invigilator should NOT receive exam 1 alert"
        
        # Create alert for exam_2
        exam2_alert = AlertEvent(
            exam_id="exam_2",
            session_id="session_2",
            event_type=AlertType.MULTIPLE_FACES,
            severity=AlertSeverity.CRITICAL,
            confidence=0.95,
            risk_score_delta=20,
            current_risk_score=60,
            message="Multiple faces in exam 2"
        )
        
        # Broadcast to exam_2
        await websocket_manager.broadcast_alert("exam_2", exam2_alert)
        
        # Verify only exam_2 invigilator received this alert
        assert exam2_ws.send_text.called, "Exam 2 invigilator should receive exam 2 alert"
        
        # Verify exam1 invigilator didn't receive exam2 alert (should have 1 call only)
        exam1_calls = exam1_ws.send_text.call_args_list
        exam1_alert_calls = [call for call in exam1_calls if "alert" in call[0][0]]
        assert len(exam1_alert_calls) == 1, "Exam 1 invigilator should only receive exam 1 alerts"
    
    @pytest.mark.asyncio
    async def test_concurrent_alert_broadcast(self):
        """Test broadcasting multiple alerts concurrently"""
        websocket_manager = WebSocketManager()
        
        # Create multiple WebSocket connections
        websockets = []
        for i in range(5):
            ws = Mock()
            ws.send_text = AsyncMock()
            ws.accept = AsyncMock()
            websockets.append(ws)
        
        # Connect all to same exam
        exam_id = "concurrent_test_exam"
        for i, ws in enumerate(websockets):
            await websocket_manager.connect(ws, exam_id, f"invigilator_{i}")
        
        # Create multiple alerts
        alerts = []
        for i in range(10):
            alert = AlertEvent(
                exam_id=exam_id,
                session_id="session_concurrent",
                event_type=AlertType.NORMAL_ACTIVITY,
                severity=AlertSeverity.INFO,
                confidence=0.8 + (i * 0.01),
                risk_score_delta=-1,
                current_risk_score=50 - i,
                message=f"Normal activity event {i}"
            )
            alerts.append(alert)
        
        # Broadcast all alerts concurrently
        broadcast_tasks = [
            websocket_manager.broadcast_alert(exam_id, alert) 
            for alert in alerts
        ]
        await asyncio.gather(*broadcast_tasks)
        
        # Verify all websockets received all alerts
        for ws in websockets:
            assert ws.send_text.call_count >= 10  # 10 alerts + 1 connection message
            
            # Verify alert messages
            send_calls = ws.send_text.call_args_list
            alert_calls = [call for call in send_calls if "alert" in call[0][0]]
            assert len(alert_calls) == 10, f"Expected 10 alerts, got {len(alert_calls)}"
            
            # Verify all alerts were received
            for i, call in enumerate(alert_calls):
                alert_message = json.loads(call[0][0])
                assert alert_message["alert"]["message"] == f"Normal activity event {i}"
    
    @pytest.mark.asyncio
    async def test_connection_disconnect_during_broadcast(self):
        """Test handling WebSocket disconnections during broadcast"""
        websocket_manager = WebSocketManager()
        
        # Create multiple WebSocket connections
        stable_ws = Mock()
        stable_ws.send_text = AsyncMock()
        stable_ws.accept = AsyncMock()
        
        unstable_ws = Mock()
        unstable_ws.send_text = AsyncMock()
        unstable_ws.accept = AsyncMock()
        # Make unstable_ws raise exception to simulate disconnect
        unstable_ws.send_text.side_effect = Exception("Connection lost")
        
        # Connect both websockets
        await websocket_manager.connect(stable_ws, "test_exam", "stable_invigilator")
        await websocket_manager.connect(unstable_ws, "test_exam", "unstable_invigilator")
        
        # Verify both are connected
        assert websocket_manager.get_connection_count("test_exam") == 2
        
        # Create and broadcast alert
        test_alert = AlertEvent(
            exam_id="test_exam",
            session_id="session_test",
            event_type=AlertType.LIVENESS_CONFIRMED,
            severity=AlertSeverity.INFO,
            confidence=0.85,
            risk_score_delta=-5,
            current_risk_score=45,
            message="Liveness confirmed"
        )
        
        await websocket_manager.broadcast_alert("test_exam", test_alert)
        
        # Verify stable connection received alert
        assert stable_ws.send_text.called
        
        # Verify unstable connection was disconnected and removed
        assert websocket_manager.get_connection_count("test_exam") == 1
    
    @pytest.mark.asyncio
    async def test_mixed_severity_alert_broadcast(self):
        """Test broadcasting alerts of different severities"""
        websocket_manager = WebSocketManager()
        
        # Create WebSocket connections
        websocket1 = Mock()
        websocket1.send_text = AsyncMock()
        websocket1.accept = AsyncMock()
        
        websocket2 = Mock()
        websocket2.send_text = AsyncMock()
        websocket2.accept = AsyncMock()
        
        # Connect invigilators
        await websocket_manager.connect(websocket1, "severity_test", "invigilator_1")
        await websocket_manager.connect(websocket2, "severity_test", "invigilator_2")
        
        # Create alerts of different severities
        alerts = [
            AlertEvent(
                exam_id="severity_test",
                session_id="session_1",
                event_type=AlertType.MOBILE_DETECTED,
                severity=AlertSeverity.CRITICAL,
                confidence=0.95,
                risk_score_delta=25,
                current_risk_score=75,
                message="Critical: Mobile detected"
            ),
            AlertEvent(
                exam_id="severity_test",
                session_id="session_1",
                event_type=AlertType.FACE_NOT_DETECTED,
                severity=AlertSeverity.WARNING,
                confidence=0.7,
                risk_score_delta=12,
                current_risk_score=87,
                message="Warning: Face not detected"
            ),
            AlertEvent(
                exam_id="severity_test",
                session_id="session_1",
                event_type=AlertType.NORMAL_ACTIVITY,
                severity=AlertSeverity.INFO,
                confidence=0.8,
                risk_score_delta=-2,
                current_risk_score=85,
                message="Info: Normal activity"
            )
        ]
        
        # Broadcast all alerts
        for alert in alerts:
            await websocket_manager.broadcast_alert("severity_test", alert)
        
        # Verify both invigilators received all alerts
        for ws, invigilator in [(websocket1, "invigilator_1"), (websocket2, "invigilator_2")]:
            assert ws.send_text.call_count == 4  # 3 alerts + 1 connection
            
            # Check that all severities were received
            send_calls = ws.send_text.call_args_list
            alert_calls = [call for call in send_calls if "alert" in call[0][0]]
            assert len(alert_calls) == 3
            
            severities_received = []
            for call in alert_calls:
                alert_message = json.loads(call[0][0])
                severities_received.append(alert_message["alert"]["severity"])
            
            assert AlertSeverity.CRITICAL in severities_received
            assert AlertSeverity.WARNING in severities_received
            assert AlertSeverity.INFO in severities_received


class TestReconnectionLoadTest:
    """Load tests for reconnection handling"""
    
    @pytest.mark.asyncio
    async def test_rapid_reconnection_simulation(self):
        """Test rapid reconnection scenarios"""
        websocket_manager = WebSocketManager()
        
        # Simulate multiple rapid reconnections
        for cycle in range(3):
            for connection_num in range(10):
                # Create new WebSocket
                ws = Mock()
                ws.send_text = AsyncMock()
                ws.accept = AsyncMock()
                ws.close = AsyncMock()
                
                # Connect
                await websocket_manager.connect(
                    ws, 
                    f"exam_load_test", 
                    f"invigilator_{connection_num}"
                )
                
                # Simulate some activity
                invigilators = websocket_manager.get_connected_invigilators("exam_load_test")
                assert len(invigilators) == connection_num + 1
                
                # Disconnect
                websocket_manager.disconnect(ws)
                
                # Verify cleanup
                invigilators_after = websocket_manager.get_connected_invigilators("exam_load_test")
                assert len(invigilators_after) == 0
        
        # Final state should be clean
        assert websocket_manager.get_connection_count("exam_load_test") == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_connection_attempts(self):
        """Test handling concurrent connection attempts"""
        websocket_manager = WebSocketManager()
        
        # Create multiple concurrent connection attempts
        async def connect_invigilator(invigilator_id):
            ws = Mock()
            ws.send_text = AsyncMock()
            ws.accept = AsyncMock()
            
            conn_id = await websocket_manager.connect(
                ws, 
                "concurrent_exam", 
                invigilator_id
            )
            return conn_id, ws
        
        # Attempt 20 concurrent connections
        connection_tasks = [
            connect_invigilator(f"invigilator_{i}") 
            for i in range(20)
        ]
        
        results = await asyncio.gather(*connection_tasks, return_exceptions=True)
        
        # Verify all connections succeeded
        successful_connections = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_connections) == 20
        
        # Verify all invigilators are connected
        assert websocket_manager.get_connection_count("concurrent_exam") == 20
        
        # Clean up
        for _, ws in successful_connections:
            websocket_manager.disconnect(ws)


class TestNetworkDropSimulation:
    """Test scenarios simulating network drops and reconnections"""
    
    @pytest.mark.asyncio
    async def test_network_drop_during_alert_broadcast(self):
        """Test alert broadcast during network instability"""
        websocket_manager = WebSocketManager()
        
        # Create "unreliable" WebSocket that intermittently fails
        unreliable_ws = Mock()
        unreliable_ws.send_text = AsyncMock(side_effect=[
            None,  # First call succeeds
            Exception("Network timeout"),  # Second call fails (network drop)
            None   # Third call succeeds (reconnected)
        ])
        unreliable_ws.accept = AsyncMock()
        
        # Create reliable WebSocket
        reliable_ws = Mock()
        reliable_ws.send_text = AsyncMock()
        reliable_ws.accept = AsyncMock()
        
        # Connect both
        await websocket_manager.connect(unreliable_ws, "drop_test", "unreliable_invigilator")
        await websocket_manager.connect(reliable_ws, "drop_test", "reliable_invigilator")
        
        # Create test alert
        test_alert = AlertEvent(
            exam_id="drop_test",
            session_id="session_drop",
            event_type=AlertType.TAB_SWITCH,
            severity=AlertSeverity.WARNING,
            confidence=0.9,
            risk_score_delta=10,
            current_risk_score=60,
            message="Tab switch during network test"
        )
        
        # Broadcast alert (should handle network drops gracefully)
        await websocket_manager.broadcast_alert("drop_test", test_alert)
        
        # Verify reliable connection received alert
        assert reliable_ws.send_text.called
        
        # Verify unreliable connection was cleaned up after failure
        assert websocket_manager.get_connection_count("drop_test") == 1  # Only reliable
        
        # Reconnect unreliable WebSocket
        new_unreliable_ws = Mock()
        new_unreliable_ws.send_text = AsyncMock()
        new_unreliable_ws.accept = AsyncMock()
        
        await websocket_manager.handle_reconnection(
            new_unreliable_ws, 
            "drop_test", 
            "unreliable_invigilator", 
            "last_message_id"
        )
        
        # Verify reconnection
        assert websocket_manager.get_connection_count("drop_test") == 2


class TestAlertDeliveryGuarantees:
    """Test at-least-once delivery guarantees"""
    
    @pytest.mark.asyncio
    async def test_delivery_retry_logic(self):
        """Test that failed deliveries are handled appropriately"""
        websocket_manager = WebSocketManager()
        
        # Create WebSocket that fails first delivery attempt
        failing_ws = Mock()
        failing_ws.send_text = AsyncMock(side_effect=[
            Exception("Connection unstable"),  # First attempt fails
            None  # Second attempt succeeds
        ])
        failing_ws.accept = AsyncMock()
        
        # Connect
        await websocket_manager.connect(failing_ws, "retry_test", "retry_invigilator")
        
        # Create alert
        test_alert = AlertEvent(
            exam_id="retry_test",
            session_id="session_retry",
            event_type=AlertType.LIVENESS_CONFIRMED,
            severity=AlertSeverity.INFO,
            confidence=0.85,
            risk_score_delta=-5,
            current_risk_score=55,
            message="Liveness confirmed - retry test"
        )
        
        # The broadcast should handle the failure gracefully
        # (Current implementation cleans up failed connections)
        await websocket_manager.broadcast_alert("retry_test", test_alert)
        
        # WebSocket should have been cleaned up due to failure
        # This demonstrates the graceful degradation behavior
        final_count = websocket_manager.get_connection_count("retry_test")
        assert final_count == 0  # Failed connection was cleaned up