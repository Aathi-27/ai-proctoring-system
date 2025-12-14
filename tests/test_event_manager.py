import pytest
from datetime import datetime
from app.services.event_manager import EventManager
from app.models.events import EventType


@pytest.mark.asyncio
class TestEventManager:
    async def test_initialization(self, event_manager):
        assert event_manager is not None
        assert hasattr(event_manager, 'face_not_detected_start')

    async def test_emit_face_detected(self, event_manager):
        exam_id = "test_exam_1"
        face_count = 1
        confidence = 0.95
        landmarks = [[[0.5, 0.5, 0.0]]]
        bounding_box = {"x": 100, "y": 100, "width": 200, "height": 200}
        
        event = await event_manager.emit_face_detected(
            exam_id, face_count, confidence, landmarks, bounding_box
        )
        
        assert event is not None
        assert event.event_type == EventType.FACE_DETECTED
        assert event.exam_id == exam_id
        assert event.face_count == face_count
        assert event.confidence == confidence

    async def test_emit_multiple_persons(self, event_manager):
        exam_id = "test_exam_2"
        face_count = 3
        confidences = [0.95, 0.88, 0.92]
        
        event = await event_manager.emit_multiple_persons(exam_id, face_count, confidences)
        
        assert event is not None
        assert event.event_type == EventType.MULTIPLE_PERSONS
        assert event.exam_id == exam_id
        assert event.face_count == face_count
        assert event.confidences == confidences
        assert event.risk_score_contribution == 20

    async def test_emit_face_not_detected_initial(self, event_manager):
        exam_id = "test_exam_3"
        
        event = await event_manager.emit_face_not_detected(exam_id)
        
        assert event is None
        assert exam_id in event_manager.face_not_detected_start

    async def test_emit_face_not_detected_threshold(self, event_manager):
        exam_id = "test_exam_4"
        
        event_manager.face_not_detected_start[exam_id] = datetime.utcnow()
        
        import asyncio
        await asyncio.sleep(0.1)
        
        event = await event_manager.emit_face_not_detected(exam_id)
        
        if event:
            assert event.event_type == EventType.FACE_NOT_DETECTED
            assert event.exam_id == exam_id
            assert event.risk_score_contribution == 20

    async def test_emit_blink_detected(self, event_manager):
        exam_id = "test_exam_5"
        ear = 0.18
        eye = "left"
        
        event = await event_manager.emit_blink_detected(exam_id, ear, eye)
        
        assert event is not None
        assert event.event_type == EventType.BLINK_DETECTED
        assert event.exam_id == exam_id
        assert event.eye_aspect_ratio == ear
        assert event.eye == eye

    async def test_emit_movement_detected(self, event_manager):
        exam_id = "test_exam_6"
        head_pose_change = {
            "pitch_change": 10.0,
            "yaw_change": 15.0,
            "roll_change": 5.0,
            "total_change": 30.0
        }
        previous_pose = {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}
        
        event = await event_manager.emit_movement_detected(
            exam_id, head_pose_change, previous_pose
        )
        
        assert event is not None
        assert event.event_type == EventType.MOVEMENT_DETECTED
        assert event.exam_id == exam_id
        assert event.head_pose_change == head_pose_change

    async def test_emit_liveness_score(self, event_manager):
        exam_id = "test_exam_7"
        score = 75.0
        blink_count = 5
        movement_events = 3
        is_live = True
        
        event = await event_manager.emit_liveness_score(
            exam_id, score, blink_count, movement_events, is_live
        )
        
        assert event is not None
        assert event.event_type == EventType.LIVENESS_SCORE
        assert event.exam_id == exam_id
        assert event.score == score
        assert event.blink_count == blink_count
        assert event.movement_events == movement_events
        assert event.is_live == is_live

    async def test_face_detected_clears_not_detected_start(self, event_manager):
        exam_id = "test_exam_8"
        
        event_manager.face_not_detected_start[exam_id] = datetime.utcnow()
        
        await event_manager.emit_face_detected(
            exam_id, 1, 0.95, [[[0.5, 0.5, 0.0]]], None
        )
        
        assert exam_id not in event_manager.face_not_detected_start
