from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EventType(str, Enum):
    FACE_DETECTED = "FACE_DETECTED"
    MULTIPLE_PERSONS = "MULTIPLE_PERSONS"
    FACE_NOT_DETECTED = "FACE_NOT_DETECTED"
    BLINK_DETECTED = "BLINK_DETECTED"
    MOVEMENT_DETECTED = "MOVEMENT_DETECTED"
    LIVENESS_SCORE = "LIVENESS_SCORE"


class FaceDetectedEvent(BaseModel):
    event_type: EventType = EventType.FACE_DETECTED
    exam_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    face_count: int
    confidence: float
    landmarks: List[List[List[float]]]
    bounding_box: Optional[Dict[str, float]] = None


class MultiplePersonsEvent(BaseModel):
    event_type: EventType = EventType.MULTIPLE_PERSONS
    exam_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    face_count: int
    confidences: List[float]
    risk_score_contribution: int = 20


class FaceNotDetectedEvent(BaseModel):
    event_type: EventType = EventType.FACE_NOT_DETECTED
    exam_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: float
    risk_score_contribution: int = 20


class BlinkDetectedEvent(BaseModel):
    event_type: EventType = EventType.BLINK_DETECTED
    exam_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    eye_aspect_ratio: float
    eye: str


class MovementDetectedEvent(BaseModel):
    event_type: EventType = EventType.MOVEMENT_DETECTED
    exam_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    head_pose_change: Dict[str, float]
    previous_pose: Optional[Dict[str, float]] = None


class LivenessScoreEvent(BaseModel):
    event_type: EventType = EventType.LIVENESS_SCORE
    exam_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    score: float
    blink_count: int
    movement_events: int
    is_live: bool


class FrameAnalysisRequest(BaseModel):
    frame_data: str
    timestamp: Optional[datetime] = None


class FrameAnalysisResponse(BaseModel):
    face_count: int
    landmarks: List[List[float]]
    liveness_score: float
    is_live: bool
    events: List[str]
    confidence_scores: List[float]
    head_pose: Optional[Dict[str, float]] = None
    processing_time_ms: float
