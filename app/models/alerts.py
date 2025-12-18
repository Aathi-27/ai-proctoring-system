from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class AlertSeverity(str, Enum):
    """Alert severity levels for prioritization"""
    INFO = "INFO"
    WARNING = "WARNING" 
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AlertType(str, Enum):
    """Types of alerts that can be generated"""
    # Critical alerts
    MOBILE_DETECTED = "MOBILE_DETECTED"
    MULTIPLE_FACES = "MULTIPLE_FACES"
    BACKGROUND_SPEECH = "BACKGROUND_SPEECH"
    
    # Warning alerts
    TAB_SWITCH = "TAB_SWITCH"
    INACTIVITY = "INACTIVITY"
    FACE_NOT_DETECTED = "FACE_NOT_DETECTED"
    
    # Info alerts
    LIVENESS_CONFIRMED = "LIVENESS_CONFIRMED"
    NORMAL_ACTIVITY = "NORMAL_ACTIVITY"
    EXAM_STARTED = "EXAM_STARTED"
    EXAM_ENDED = "EXAM_ENDED"


class AlertEvent(BaseModel):
    """Alert event structure as specified in requirements"""
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: AlertType
    severity: AlertSeverity
    confidence: float = Field(ge=0.0, le=1.0)
    risk_score_delta: int
    current_risk_score: int = Field(ge=0, le=100)
    message: str
    evidence_snapshot_id: Optional[str] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class EvidenceSnapshot(BaseModel):
    """Evidence snapshot metadata and storage information"""
    snapshot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    session_id: str
    alert_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: AlertType
    frame_number: int
    risk_score: int
    file_path: str
    file_size: int
    encryption_key_id: Optional[str] = None
    retention_expires_at: datetime


class InvigilatorConnection(BaseModel):
    """WebSocket connection information for an invigilator"""
    connection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    invigilator_id: str
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_id: Optional[str] = None
    status: str = "connected"


class AlertAcknowledgmentRequest(BaseModel):
    """Request to acknowledge an alert"""
    alert_id: str
    invigilator_id: str


class AlertQueryRequest(BaseModel):
    """Request to query alert history"""
    exam_id: str
    session_id: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    event_type: Optional[AlertType] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)