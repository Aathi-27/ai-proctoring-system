from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class MessageType(str, Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    ALERT = "alert"
    VIDEO_FRAME = "video_frame"
    AUDIO_CHUNK = "audio_chunk"
    CANDIDATE_STATUS = "candidate_status"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    STREAM_QUALITY = "stream_quality"
    CONNECTION_STATUS = "connection_status"
    PING = "ping"
    PONG = "pong"


class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class WebSocketMessage(BaseModel):
    type: MessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertMessage(BaseModel):
    level: AlertLevel
    message: str
    candidate_id: Optional[str] = None
    session_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class VideoFrameMessage(BaseModel):
    session_id: str
    frame_data: str
    frame_number: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    quality: Optional[str] = "medium"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AudioChunkMessage(BaseModel):
    session_id: str
    audio_data: str
    chunk_number: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sample_rate: Optional[int] = 48000

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CandidateStatusMessage(BaseModel):
    session_id: str
    candidate_id: str
    status: str
    has_video: bool = False
    has_audio: bool = False
    network_quality: Optional[str] = "good"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StreamQualityMessage(BaseModel):
    session_id: str
    video_quality: str
    fps: int
    bandwidth_kbps: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
