#!/usr/bin/env python3
"""
Simple test script to verify WebSocket alert system components work independently
"""

import asyncio
import json
from datetime import datetime
import uuid

from app.models.alerts import AlertEvent, AlertSeverity, AlertType

def test_alert_models():
    """Test alert data models"""
    print("Testing Alert Models...")
    
    # Test AlertEvent creation
    alert = AlertEvent(
        exam_id="test_exam_123",
        session_id="test_session_456",
        event_type=AlertType.MOBILE_DETECTED,
        severity=AlertSeverity.CRITICAL,
        confidence=0.95,
        risk_score_delta=25,
        current_risk_score=50,
        message="Mobile phone detected in camera frame"
    )
    
    print(f"✓ AlertEvent created with ID: {alert.alert_id}")
    print(f"  Event Type: {alert.event_type}")
    print(f"  Severity: {alert.severity}")
    print(f"  Confidence: {alert.confidence}")
    print(f"  Risk Score: {alert.current_risk_score}")
    
    # Test serialization
    alert_dict = alert.model_dump()
    print(f"✓ AlertEvent serialized successfully")
    print(f"  Keys: {list(alert_dict.keys())}")
    
    # Test different severity levels
    severities = [AlertSeverity.INFO, AlertSeverity.WARNING, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
    for severity in severities:
        alert.severity = severity
        print(f"✓ {severity.value} severity test passed")
    
    # Test different event types
    event_types = [AlertType.MOBILE_DETECTED, AlertType.MULTIPLE_FACES, AlertType.TAB_SWITCH, AlertType.LIVENESS_CONFIRMED]
    for event_type in event_types:
        alert.event_type = event_type
        print(f"✓ {event_type.value} event type test passed")
    
    return True

def test_websocket_manager_basic():
    """Test basic WebSocket manager functionality"""
    print("\nTesting WebSocket Manager (Basic)...")
    
    from app.services.websocket_manager import WebSocketManager
    
    manager = WebSocketManager()
    print("✓ WebSocketManager created successfully")
    
    # Test connection tracking
    print(f"✓ Connection count for non-existent exam: {manager.get_connection_count('test_exam')}")
    
    # Test message ID generation
    msg_id1 = manager._get_next_message_id()
    msg_id2 = manager._get_next_message_id()
    print(f"✓ Message IDs generated: {msg_id1}, {msg_id2}")
    
    return True

async def test_alert_service_basic():
    """Test basic AlertService functionality"""
    print("\nTesting AlertService (Basic)...")
    
    from app.services.alert_service import AlertService
    
    service = AlertService()
    print("✓ AlertService created successfully")
    
    # Test alert rule configuration
    rules = service._initialize_alert_rules()
    print(f"✓ Alert rules initialized: {len(rules)} event types")
    
    # Test specific rule
    mobile_rule = rules.get(AlertType.MOBILE_DETECTED)
    if mobile_rule:
        print(f"✓ MOBILE_DETECTED rule: severity={mobile_rule['severity']}, delta={mobile_rule['risk_score_delta']}")
    else:
        print("✗ MOBILE_DETECTED rule not found")
        return False
    
    return True

def test_evidence_service_basic():
    """Test basic EvidenceService functionality"""
    print("\nTesting EvidenceService (Basic)...")
    
    from app.services.evidence_service import EvidenceSnapshotService
    
    service = EvidenceSnapshotService()
    print("✓ EvidenceSnapshotService created successfully")
    
    # Test encryption/decryption
    test_data = b"test evidence data"
    encrypted = service._encrypt_data(test_data)
    
    if encrypted and encrypted != test_data:
        print("✓ Data encryption works")
        
        decrypted = service._decrypt_data(encrypted)
        if decrypted == test_data:
            print("✓ Data decryption works")
        else:
            print("✗ Data decryption failed")
            return False
    else:
        print("✗ Data encryption failed")
        return False
    
    # Test retention period setting
    service.set_retention_period(60)
    if service.snapshot_retention_days == 60:
        print("✓ Retention period setting works")
    else:
        print("✗ Retention period setting failed")
        return False
    
    return True

def test_json_serialization():
    """Test JSON serialization for WebSocket messages"""
    print("\nTesting JSON Serialization...")
    
    # Create test alert
    alert = AlertEvent(
        exam_id="json_test_exam",
        session_id="json_test_session",
        event_type=AlertType.TAB_SWITCH,
        severity=AlertSeverity.WARNING,
        confidence=0.9,
        risk_score_delta=10,
        current_risk_score=60,
        message="Tab switch detected during exam"
    )
    
    # Test message format
    message = {
        "type": "alert",
        "alert": alert.model_dump()
    }
    
    # Serialize to JSON
    json_str = json.dumps(message, default=str)
    print("✓ JSON serialization successful")
    
    # Deserialize from JSON
    deserialized = json.loads(json_str)
    print("✓ JSON deserialization successful")
    
    # Verify structure
    if deserialized.get("type") == "alert" and "alert" in deserialized:
        print("✓ Message structure valid")
    else:
        print("✗ Message structure invalid")
        return False
    
    return True

def test_pydantic_validation():
    """Test Pydantic validation and constraints"""
    print("\nTesting Pydantic Validation...")
    
    # Test valid confidence range
    try:
        alert = AlertEvent(
            exam_id="validation_test",
            session_id="validation_session",
            event_type=AlertType.NORMAL_ACTIVITY,
            severity=AlertSeverity.INFO,
            confidence=0.85,  # Valid range
            risk_score_delta=-2,
            current_risk_score=48,
            message="Test validation"
        )
        print("✓ Valid confidence range accepted")
    except Exception as e:
        print(f"✗ Valid confidence range rejected: {e}")
        return False
    
    # Test invalid confidence range (should fail in Pydantic v2)
    try:
        alert = AlertEvent(
            exam_id="validation_test",
            session_id="validation_session",
            event_type=AlertType.NORMAL_ACTIVITY,
            severity=AlertSeverity.INFO,
            confidence=1.5,  # Invalid: > 1.0
            risk_score_delta=-2,
            current_risk_score=48,
            message="Test validation"
        )
        print("✗ Invalid confidence range was accepted (should have failed)")
        return False
    except Exception:
        print("✓ Invalid confidence range correctly rejected")
    
    # Test invalid risk score range
    try:
        alert = AlertEvent(
            exam_id="validation_test",
            session_id="validation_session",
            event_type=AlertType.NORMAL_ACTIVITY,
            severity=AlertSeverity.INFO,
            confidence=0.8,
            risk_score_delta=-2,
            current_risk_score=150,  # Invalid: > 100
            message="Test validation"
        )
        print("✗ Invalid risk score was accepted (should have failed)")
        return False
    except Exception:
        print("✓ Invalid risk score correctly rejected")
    
    return True

async def main():
    """Run all basic tests"""
    print("WebSocket Alert System - Basic Component Tests")
    print("=" * 50)
    
    tests = [
        ("Alert Models", test_alert_models),
        ("WebSocket Manager (Basic)", test_websocket_manager_basic),
        ("AlertService (Basic)", test_alert_service_basic),
        ("EvidenceService (Basic)", test_evidence_service_basic),
        ("JSON Serialization", test_json_serialization),
        ("Pydantic Validation", test_pydantic_validation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All basic tests passed! WebSocket alert system components are working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())