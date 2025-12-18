from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "exam_monitoring"
    collection_name: str = "monitoring_events"
    cors_origins: list = ["http://localhost:3000", "http://localhost:3001"]
    websocket_heartbeat_interval: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
