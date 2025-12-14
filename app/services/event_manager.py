from datetime import datetime
from typing import Dict, Any, List
from app.database.mongodb import MongoDBClient
from app.models.events import (
    EventType,
    FaceDetectedEvent,
    MultiplePersonsEvent,
    FaceNotDetectedEvent,
    BlinkDetectedEvent,
    MovementDetectedEvent,
    LivenessScoreEvent
)


class EventManager:
    def __init__(self):
        self.face_not_detected_start = {}

    async def emit_face_detected(self, exam_id: str, face_count: int, confidence: float, 
                                 landmarks: List[List[float]], bounding_box: Dict[str, float] = None):
        event = FaceDetectedEvent(
            exam_id=exam_id,
            face_count=face_count,
            confidence=confidence,
            landmarks=landmarks,
            bounding_box=bounding_box
        )
        await self._save_event(event.model_dump())
        
        if exam_id in self.face_not_detected_start:
            del self.face_not_detected_start[exam_id]
        
        return event

    async def emit_multiple_persons(self, exam_id: str, face_count: int, confidences: List[float]):
        event = MultiplePersonsEvent(
            exam_id=exam_id,
            face_count=face_count,
            confidences=confidences
        )
        await self._save_event(event.model_dump())
        return event

    async def emit_face_not_detected(self, exam_id: str):
        current_time = datetime.utcnow()
        
        if exam_id not in self.face_not_detected_start:
            self.face_not_detected_start[exam_id] = current_time
            return None
        
        duration = (current_time - self.face_not_detected_start[exam_id]).total_seconds()
        
        if duration >= 5:
            event = FaceNotDetectedEvent(
                exam_id=exam_id,
                duration_seconds=duration
            )
            await self._save_event(event.model_dump())
            self.face_not_detected_start[exam_id] = current_time
            return event
        
        return None

    async def emit_blink_detected(self, exam_id: str, eye_aspect_ratio: float, eye: str):
        event = BlinkDetectedEvent(
            exam_id=exam_id,
            eye_aspect_ratio=eye_aspect_ratio,
            eye=eye
        )
        await self._save_event(event.model_dump())
        return event

    async def emit_movement_detected(self, exam_id: str, head_pose_change: Dict[str, float], 
                                    previous_pose: Dict[str, float] = None):
        event = MovementDetectedEvent(
            exam_id=exam_id,
            head_pose_change=head_pose_change,
            previous_pose=previous_pose
        )
        await self._save_event(event.model_dump())
        return event

    async def emit_liveness_score(self, exam_id: str, score: float, blink_count: int, 
                                 movement_events: int, is_live: bool):
        event = LivenessScoreEvent(
            exam_id=exam_id,
            score=score,
            blink_count=blink_count,
            movement_events=movement_events,
            is_live=is_live
        )
        await self._save_event(event.model_dump())
        return event

    async def _save_event(self, event_data: Dict[str, Any]):
        collection = MongoDBClient.get_events_collection()
        await collection.insert_one(event_data)

    async def get_events(self, exam_id: str, event_type: EventType = None, limit: int = 100):
        collection = MongoDBClient.get_events_collection()
        query = {"exam_id": exam_id}
        if event_type:
            query["event_type"] = event_type
        
        cursor = collection.find(query).sort("timestamp", -1).limit(limit)
        events = await cursor.to_list(length=limit)
        return events
