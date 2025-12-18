from pydantic_settings import BaseSettings
from typing import Dict


class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "exam_proctoring"
    risk_score_window_minutes: int = 5
    time_decay_factor: float = 0.5
    
    weight_multiple_persons: int = 30
    weight_mobile_detected: int = 25
    weight_background_speech: int = 15
    weight_tab_switched: int = 10
    weight_face_not_detected: int = 20
    weight_copy_detected: int = 5
    weight_paste_detected: int = 5
    weight_keyboard_inactivity: int = 2
    weight_tablet_detected: int = 20
    weight_multiple_voices: int = 15
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def event_weights(self) -> Dict[str, int]:
        return {
            "MULTIPLE_PERSONS": self.weight_multiple_persons,
            "MOBILE_DETECTED": self.weight_mobile_detected,
            "BACKGROUND_SPEECH": self.weight_background_speech,
            "TAB_SWITCHED": self.weight_tab_switched,
            "FACE_NOT_DETECTED": self.weight_face_not_detected,
            "COPY_DETECTED": self.weight_copy_detected,
            "PASTE_DETECTED": self.weight_paste_detected,
            "KEYBOARD_INACTIVITY": self.weight_keyboard_inactivity,
            "TABLET_DETECTED": self.weight_tablet_detected,
            "MULTIPLE_VOICES": self.weight_multiple_voices,
        }


settings = Settings()
