from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Exam Proctoring System"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "exam_proctoring"
    EVENTS_COLLECTION: str = "events"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Face Detection
    FACE_DETECTION_CONFIDENCE: float = 0.5
    MAX_NUM_FACES: int = 5
    
    # Liveness
    FACE_NOT_DETECTED_THRESHOLD: int = 5
    BLINK_EAR_THRESHOLD: float = 0.2
    MOVEMENT_THRESHOLD: float = 10.0
    
    # Processing
    LIVENESS_WINDOW_SECONDS: int = 30
    TARGET_FPS: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
