"""
Data models for YOLOv8 detection system.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DetectionEventType(Enum):
    """Enumeration of detection event types."""
    MOBILE_DETECTED = "MOBILE_DETECTED"
    TABLET_DETECTED = "TABLET_DETECTED"
    SUSPICIOUS_OBJECT = "SUSPICIOUS_OBJECT"
    PERSON_DETECTED = "PERSON_DETECTED"


@dataclass
class DetectionResult:
    """Result from object detection."""
    class_name: str
    confidence: float
    bbox: tuple  # (x, y, width, height)
    area_ratio: float
    timestamp: float
    frame_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "class_name": self.class_name,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "area_ratio": self.area_ratio,
            "timestamp": self.timestamp,
            "frame_id": self.frame_id
        }


@dataclass
class DetectionEvent:
    """Event generated from detection results."""
    event_type: str
    object_type: str
    confidence: float
    bbox: tuple  # (x, y, width, height)
    timestamp: float
    frame_id: Optional[int] = None
    risk_score: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "object_type": self.object_type,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "timestamp": self.timestamp,
            "frame_id": self.frame_id,
            "risk_score": self.risk_score,
            "metadata": self.metadata or {}
        }


@dataclass
class ProcessFrameResponse:
    """Response model for frame processing endpoint."""
    detected_objects: List[DetectionResult]
    events: List[DetectionEvent]
    processing_time_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "detected_objects": [obj.to_dict() for obj in self.detected_objects],
            "events": [event.to_dict() for event in self.events],
            "processing_time_ms": self.processing_time_ms
        }


@dataclass
class APIResponse:
    """Standard API response structure."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: float = datetime.now().timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp
        }