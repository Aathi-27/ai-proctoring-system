import asyncio
import json
import sys
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# Test the complete alert generation and broadcasting workflow
async def test_alert_workflow():
    """Test the complete alert workflow from generation to broadcast"""
    print("Testing Complete Alert Workflow...")
    
    from app.models.alerts import AlertEvent, AlertSeverity, AlertType
    from app.services.alert_service import AlertService
    from app.services.websocket_manager import WebSocketManager
    from app.services.evidence_service import EvidenceSnapshotService
    
    # Create services
    alert_service = AlertService()
    websocket_manager = WebSocketManager()
    evidence_service = EvidenceSnapshotService()
    
    # Mock WebSocket for testing
    mock_websocket = Mock()
    mock_websocket.send_text = AsyncMock()
    mock_websocket.accept = AsyncMock()
    
    # Test 1: Connect WebSocket
    exam_id = "workflow_test_exam"
    session_id = "workflow_test_session"
    invigilator_id = "test_invigilator"
    
    connection_id = await websocket_manager.connect(mock_websocket, exam_id, invigilator_id)
    print(f"✓ WebSocket connected: {connection_id}")
    
    # Test 2: Generate critical alert
    mock_frame_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="  # 1x1 pixel PNG
    
    with patch.object(alert_service, '_store_alert', return_value=True), \
         patch.object(alert_service, '_calculate_risk_score', return_value=30), \
         patch.object(alert_service, '_update_risk_score_cache', return_value=None):
        
        alert = await alert_service.generate_alert(
            exam_id=exam_id,
            session_id=session_id,
            event_type=AlertType.MOBILE_DETECTED,
            confidence=0.95,
            frame_data=mock_frame_data,
            frame_number=42
        )
    
    if alert:
        print(f"✓ Alert generated: {alert.event_type} (ID: {alert.alert_id[:8]}...)")
        print(f"  Severity: {alert.severity}")
        print(f"  Risk Score: {alert.current_risk_score}")
        print(f"  Message: {alert.message}")
    else:
        print("✗ Alert generation failed")
        return False
    
    # Test 3: Verify WebSocket broadcast
    if mock_websocket.send_text.called:
        sent_message = json.loads(mock_websocket.send_text.call_args[0][0])
        if sent_message.get("type") == "alert":
            print("✓ Alert broadcast via WebSocket")
            alert_data = sent_message.get("alert", {})
            if alert_data.get("event_type") == AlertType.MOBILE_DETECTED:
                print("✓ Broadcast contains correct alert data")
            else:
                print("✗ Broadcast alert data incorrect")
                return False
        else:
            print("✗ WebSocket message type incorrect")
            return False
    else:
        print("✗ WebSocket not called for broadcast")
        return False
    
    # Test 4: Test alert acknowledgment
    success = await alert_service.acknowledge_alert(alert.alert_id, invigilator_id)
    if success:
        print("✓ Alert acknowledgment successful")
    else:
        print("✗ Alert acknowledgment failed")
        return False
    
    # Test 5: Test evidence snapshot capture
    snapshot = await evidence_service.capture_snapshot(
        frame_data=mock_frame_data,
        exam_id=exam_id,
        session_id=session_id,
        alert_id=alert.alert_id,
        event_type=alert.event_type,
        frame_number=42,
        risk_score=alert.current_risk_score
    )
    
    if snapshot:
        print(f"✓ Evidence snapshot captured: {snapshot.snapshot_id}")
        print(f"  File path: {snapshot.file_path}")
        print(f"  File size: {snapshot.file_size} bytes")
    else:
        print("✗ Evidence snapshot capture failed")
        return False
    
    # Test 6: Test multiple severity levels
    alert_types_to_test = [
        (AlertType.TAB_SWITCH, AlertSeverity.WARNING),
        (AlertType.LIVENESS_CONFIRMED, AlertSeverity.INFO),
        (AlertType.MULTIPLE_FACES, AlertSeverity.CRITICAL)
    ]
    
    for event_type, expected_severity in alert_types_to_test:
        with patch.object(alert_service, '_store_alert', return_value=True), \
             patch.object(alert_service, '_calculate_risk_score', return_value=40), \
             patch.object(alert_service, '_update_risk_score_cache', return_value=None):
            
            test_alert = await alert_service.generate_alert(
                exam_id=exam_id,
                session_id=session_id,
                event_type=event_type,
                confidence=0.85
            )
        
        if test_alert and test_alert.severity == expected_severity:
            print(f"✓ {event_type.value} -> {expected_severity.value} severity mapping correct")
        else:
            print(f"✗ {event_type.value} severity mapping incorrect")
            return False
    
    # Test 7: Test risk score calculation
    risk_score = await alert_service.get_risk_score(exam_id)
    print(f"✓ Risk score calculated: {risk_score}")
    
    # Test 8: Test exam monitoring lifecycle
    start_success = await alert_service.start_exam_monitoring(exam_id, session_id)
    if start_success:
        print("✓ Exam monitoring started")
    else:
        print("✗ Exam monitoring start failed")
        return False
    
    end_success = await alert_service.end_exam_monitoring(exam_id, session_id)
    if end_success:
        print("✓ Exam monitoring ended")
    else:
        print("✗ Exam monitoring end failed")
        return False
    
    # Test 9: Test connection management
    invigilators = websocket_manager.get_connected_invigilators(exam_id)
    connection_count = websocket_manager.get_connection_count(exam_id)
    print(f"✓ Connected invigilators: {len(invigilators)}, Connection count: {connection_count}")
    
    # Test 10: Test JSON message protocol
    test_message = {
        "type": "test_message",
        "exam_id": exam_id,
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "data": "test_payload"
    }
    
    await websocket_manager.send_personal_message(mock_websocket, test_message)
    if mock_websocket.send_text.called:
        print("✓ Personal message sending works")
        
        # Verify message includes required protocol fields
        sent_text = mock_websocket.send_text.call_args[0][0]
        sent_data = json.loads(sent_text)
        if "message_id" in sent_data and "server_timestamp" in sent_data:
            print("✓ Message protocol fields present (message_id, server_timestamp)")
        else:
            print("✗ Message protocol fields missing")
            return False
    else:
        print("✗ Personal message sending failed")
        return False
    
    print("\n✅ Complete alert workflow test passed!")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_alert_workflow())
    if result:
        print("\n🎉 All workflow tests successful! The WebSocket alert system is fully functional.")
        sys.exit(0)
    else:
        print("\n❌ Workflow tests failed. Please check the implementation.")
        sys.exit(1)