"""
Configuration settings for YOLOv8 mobile detection system.
"""

from typing import Dict, Any
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    from pydantic import BaseSettings, Field


class DetectionConfig(BaseSettings):
    """Configuration for YOLOv8 detection system."""
    
    model_name: str = Field(default="yolov8n.pt", description="YOLOv8 model variant")
    model_confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    frame_skip_ratio: int = Field(default=3, ge=1, le=10)
    max_processing_time_ms: int = Field(default=500, ge=100, le=2000)
    
    # Target classes for detection
    target_classes: list = Field(
        default=["mobile_phone", "tablet", "laptop", "notebook", "person"]
    )
    
    # Risk scoring
    mobile_phone_risk_points: int = Field(default=25, ge=0, le=100)
    tablet_risk_points: int = Field(default=20, ge=0, le=100)
    laptop_risk_points: int = Field(default=15, ge=0, le=100)
    notebook_risk_points: int = Field(default=10, ge=0, le=50)
    
    # Temporal filtering
    temporal_window: int = Field(default=3, ge=2, le=10)
    min_consecutive_frames: int = Field(default=2, ge=1, le=5)
    
    # CPU optimization
    use_fp16: bool = Field(default=True)
    input_size: tuple = Field(default=(640, 640))
    
    class Config:
        env_prefix = "DETECTION_"


class MongoDBConfig(BaseSettings):
    """MongoDB configuration."""
    
    host: str = Field(default="localhost")
    port: int = Field(default=27017, ge=1, le=65535)
    database: str = Field(default="exam_detection")
    collection: str = Field(default="detection_events")
    username: str = Field(default="")
    password: str = Field(default="")
    
    class Config:
        env_prefix = "MONGODB_"


class APIConfig(BaseSettings):
    """API configuration."""
    
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1024, le=65535)
    debug: bool = Field(default=False)
    max_file_size_mb: int = Field(default=50)
    allowed_extensions: list = Field(default=[".jpg", ".jpeg", ".png", ".bmp"])
    
    class Config:
        env_prefix = "API_"


# Global configuration instances
detection_config = DetectionConfig()
mongodb_config = MongoDBConfig()
api_config = APIConfig()