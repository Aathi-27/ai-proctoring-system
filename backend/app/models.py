from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class MonitoringEventType(str, Enum):
    TAB_SWITCHED = "TAB_SWITCHED"
    COPY_DETECTED = "COPY_DETECTED"
    PASTE_DETECTED = "PASTE_DETECTED"
    KEYBOARD_INACTIVITY = "KEYBOARD_INACTIVITY"
    MOUSE_INACTIVITY = "MOUSE_INACTIVITY"
    ACTIVITY_RESUMED = "ACTIVITY_RESUMED"


class BaseMonitoringEvent(BaseModel):
    type: MonitoringEventType
    timestamp: int
    session_id: Optional[str] = Field(None, alias="sessionId")
    candidate_id: Optional[str] = Field(None, alias="candidateId")
    
    class Config:
        populate_by_name = True


class TabSwitchedEvent(BaseMonitoringEvent):
    type: Literal[MonitoringEventType.TAB_SWITCHED]
    inactive_duration: int


class ClipboardEvent(BaseMonitoringEvent):
    type: Literal[MonitoringEventType.COPY_DETECTED, MonitoringEventType.PASTE_DETECTED]
    content_length: int


class InactivityEvent(BaseMonitoringEvent):
    type: Literal[MonitoringEventType.KEYBOARD_INACTIVITY, MonitoringEventType.MOUSE_INACTIVITY]
    duration_seconds: int


class ActivityResumedEvent(BaseMonitoringEvent):
    type: Literal[MonitoringEventType.ACTIVITY_RESUMED]


class MonitoringEventDocument(BaseModel):
    event_type: str
    timestamp: int
    session_id: Optional[str] = None
    candidate_id: Optional[str] = None
    inactive_duration: Optional[int] = None
    content_length: Optional[int] = None
    duration_seconds: Optional[int] = None
    received_at: datetime = Field(default_factory=datetime.utcnow)
    server_timestamp: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp() * 1000))

    def to_dict(self):
        return self.model_dump(exclude_none=True)
