from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "exam_proctoring"
    events_collection: str = "events"
    
    face_detection_confidence: float = 0.5
    max_num_faces: int = 5
    
    face_not_detected_threshold: int = 5
    blink_ear_threshold: float = 0.2
    movement_threshold: float = 10.0
    
    liveness_window_seconds: int = 30
    target_fps: int = 10
    
    class Config:
        env_file = ".env"


settings = Settings()
