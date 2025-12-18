from typing import Dict, List, Any
from datetime import datetime
from src.config import (
    EVENT_VAD_DETECTED,
    EVENT_SPEECH_SILENCE_RATIO,
    EVENT_BACKGROUND_SPEECH,
    EVENT_MULTIPLE_VOICES,
    EVENT_NOISE_SPIKE,
)


class AudioEvent:
    """Represents an audio event."""

    def __init__(
        self, event_type: str, data: Dict[str, Any], timestamp: datetime = None
    ):
        """
        Initialize audio event.

        Args:
            event_type: Type of event
            data: Event data
            timestamp: Event timestamp (defaults to now)
        """
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary.

        Returns:
            Event as dictionary
        """
        return {
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }


class AudioEventManager:
    """Manages audio event creation and aggregation."""

    def __init__(self):
        """Initialize event manager."""
        self.events: List[AudioEvent] = []

    def create_vad_detected_event(
        self, confidence: float, timestamp: datetime = None
    ) -> AudioEvent:
        """
        Create VAD detected event.

        Args:
            confidence: VAD confidence score (0-1)
            timestamp: Event timestamp

        Returns:
            Audio event
        """
        event = AudioEvent(
            EVENT_VAD_DETECTED,
            {"confidence": float(confidence)},
            timestamp,
        )
        self.events.append(event)
        return event

    def create_speech_silence_ratio_event(
        self, speech_pct: float, silence_pct: float, window_s: float, timestamp: datetime = None
    ) -> AudioEvent:
        """
        Create speech/silence ratio event.

        Args:
            speech_pct: Percentage of speech
            silence_pct: Percentage of silence
            window_s: Analysis window duration in seconds
            timestamp: Event timestamp

        Returns:
            Audio event
        """
        event = AudioEvent(
            EVENT_SPEECH_SILENCE_RATIO,
            {
                "speech_pct": float(speech_pct),
                "silence_pct": float(silence_pct),
                "window_s": float(window_s),
            },
            timestamp,
        )
        self.events.append(event)
        return event

    def create_background_speech_event(
        self, confidence: float, timestamp: datetime = None
    ) -> AudioEvent:
        """
        Create background speech detected event.

        Args:
            confidence: Detection confidence score (0-1)
            timestamp: Event timestamp

        Returns:
            Audio event
        """
        event = AudioEvent(
            EVENT_BACKGROUND_SPEECH,
            {"confidence": float(confidence)},
            timestamp,
        )
        self.events.append(event)
        return event

    def create_multiple_voices_event(
        self, speaker_count: int, confidence: float, timestamp: datetime = None
    ) -> AudioEvent:
        """
        Create multiple voices detected event.

        Args:
            speaker_count: Estimated number of speakers
            confidence: Detection confidence score (0-1)
            timestamp: Event timestamp

        Returns:
            Audio event
        """
        event = AudioEvent(
            EVENT_MULTIPLE_VOICES,
            {
                "speaker_count": int(speaker_count),
                "confidence": float(confidence),
            },
            timestamp,
        )
        self.events.append(event)
        return event

    def create_noise_spike_event(
        self, decibel_level: float, duration_ms: float, timestamp: datetime = None
    ) -> AudioEvent:
        """
        Create noise spike event.

        Args:
            decibel_level: Noise level in dB
            duration_ms: Duration of spike in milliseconds
            timestamp: Event timestamp

        Returns:
            Audio event
        """
        event = AudioEvent(
            EVENT_NOISE_SPIKE,
            {
                "decibel_level": float(decibel_level),
                "duration_ms": float(duration_ms),
            },
            timestamp,
        )
        self.events.append(event)
        return event

    def get_events(self) -> List[Dict[str, Any]]:
        """
        Get all events as dictionaries.

        Returns:
            List of events
        """
        return [event.to_dict() for event in self.events]

    def clear_events(self) -> None:
        """Clear event history."""
        self.events.clear()

    def get_events_by_type(self, event_type: str) -> List[AudioEvent]:
        """
        Get events of a specific type.

        Args:
            event_type: Type of event to filter

        Returns:
            List of events of that type
        """
        return [event for event in self.events if event.event_type == event_type]
