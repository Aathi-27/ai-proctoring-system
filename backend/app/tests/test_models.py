import pytest
from app.models import (
    MonitoringEventType,
    TabSwitchedEvent,
    ClipboardEvent,
    InactivityEvent,
    ActivityResumedEvent,
    MonitoringEventDocument,
)


def test_tab_switched_event():
    event = TabSwitchedEvent(
        type=MonitoringEventType.TAB_SWITCHED,
        timestamp=1234567890,
        session_id="test-session",
        candidate_id="test-candidate",
        inactive_duration=5000,
    )
    
    assert event.type == MonitoringEventType.TAB_SWITCHED
    assert event.timestamp == 1234567890
    assert event.session_id == "test-session"
    assert event.candidate_id == "test-candidate"
    assert event.inactive_duration == 5000


def test_clipboard_event_copy():
    event = ClipboardEvent(
        type=MonitoringEventType.COPY_DETECTED,
        timestamp=1234567890,
        session_id="test-session",
        candidate_id="test-candidate",
        content_length=100,
    )
    
    assert event.type == MonitoringEventType.COPY_DETECTED
    assert event.content_length == 100


def test_clipboard_event_paste():
    event = ClipboardEvent(
        type=MonitoringEventType.PASTE_DETECTED,
        timestamp=1234567890,
        session_id="test-session",
        candidate_id="test-candidate",
        content_length=50,
    )
    
    assert event.type == MonitoringEventType.PASTE_DETECTED
    assert event.content_length == 50


def test_inactivity_event():
    event = InactivityEvent(
        type=MonitoringEventType.KEYBOARD_INACTIVITY,
        timestamp=1234567890,
        session_id="test-session",
        candidate_id="test-candidate",
        duration_seconds=30,
    )
    
    assert event.type == MonitoringEventType.KEYBOARD_INACTIVITY
    assert event.duration_seconds == 30


def test_activity_resumed_event():
    event = ActivityResumedEvent(
        type=MonitoringEventType.ACTIVITY_RESUMED,
        timestamp=1234567890,
        session_id="test-session",
        candidate_id="test-candidate",
    )
    
    assert event.type == MonitoringEventType.ACTIVITY_RESUMED


def test_monitoring_event_document():
    doc = MonitoringEventDocument(
        event_type=MonitoringEventType.TAB_SWITCHED.value,
        timestamp=1234567890,
        session_id="test-session",
        candidate_id="test-candidate",
        inactive_duration=5000,
    )
    
    assert doc.event_type == "TAB_SWITCHED"
    assert doc.timestamp == 1234567890
    assert doc.session_id == "test-session"
    assert doc.candidate_id == "test-candidate"
    assert doc.inactive_duration == 5000
    assert doc.received_at is not None
    assert doc.server_timestamp > 0


def test_monitoring_event_document_to_dict():
    doc = MonitoringEventDocument(
        event_type=MonitoringEventType.COPY_DETECTED.value,
        timestamp=1234567890,
        session_id="test-session",
        candidate_id="test-candidate",
        content_length=100,
    )
    
    doc_dict = doc.to_dict()
    
    assert doc_dict["event_type"] == "COPY_DETECTED"
    assert doc_dict["timestamp"] == 1234567890
    assert doc_dict["session_id"] == "test-session"
    assert doc_dict["candidate_id"] == "test-candidate"
    assert doc_dict["content_length"] == 100
    assert "received_at" in doc_dict
    assert "server_timestamp" in doc_dict
    assert "inactive_duration" not in doc_dict
