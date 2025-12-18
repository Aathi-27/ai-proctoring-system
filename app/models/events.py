from pydantic import BaseModel, Field, validator
from typing import Literal
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    MULTIPLE_PERSONS = "MULTIPLE_PERSONS"
    MOBILE_DETECTED = "MOBILE_DETECTED"
    BACKGROUND_SPEECH = "BACKGROUND_SPEECH"
    TAB_SWITCHED = "TAB_SWITCHED"
    FACE_NOT_DETECTED = "FACE_NOT_DETECTED"
    COPY_DETECTED = "COPY_DETECTED"
    PASTE_DETECTED = "PASTE_DETECTED"
    KEYBOARD_INACTIVITY = "KEYBOARD_INACTIVITY"
    TABLET_DETECTED = "TABLET_DETECTED"
    MULTIPLE_VOICES = "MULTIPLE_VOICES"


class DetectionEvent(BaseModel):
    exam_id: str
    session_id: str
    event_type: EventType
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v


class EventContribution(BaseModel):
    event: str
    confidence: float
    weight: int
    contribution: float
    timestamp: datetime


class RiskScore(BaseModel):
    exam_id: str
    session_id: str
    score: float = Field(ge=0.0, le=100.0)
    risk_level: Literal["Low", "Medium", "High", "Critical"]
    contribution_breakdown: list[EventContribution]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @staticmethod
    def get_risk_level(score: float) -> str:
        if score <= 30:
            return "Low"
        elif score <= 60:
            return "Medium"
        elif score <= 85:
            return "High"
        else:
            return "Critical"


class RiskScoreResponse(BaseModel):
    exam_id: str
    session_id: str
    current_score: float
    risk_level: str
    last_updated: datetime
    contribution_breakdown: list[EventContribution]


class RiskTimelineResponse(BaseModel):
    exam_id: str
    session_id: str
    timeline: list[RiskScore]


class ScoreBreakdownResponse(BaseModel):
    exam_id: str
    session_id: str
    current_score: float
    risk_level: str
    total_events: int
    contribution_breakdown: list[EventContribution]
    active_events_in_window: int
