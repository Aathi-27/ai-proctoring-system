import numpy as np
from typing import Dict, List, Tuple, Any
from datetime import datetime
from src.vad import VoiceActivityDetector
from src.preprocessing import AudioPreprocessor
from src.voice_detector import VoiceDetector
from src.audio_buffer import AudioBuffer
from src.audio_events import AudioEventManager, AudioEvent
from src.database import MongoDBManager
from src.config import SAMPLE_RATE, FRAME_DURATION_MS


class AudioAnalysisPipeline:
    """
    Complete real-time audio analysis pipeline for VAD, voice detection, and event logging.
    """

    def __init__(self, exam_id: str = None):
        """
        Initialize audio pipeline.

        Args:
            exam_id: Exam ID for database logging
        """
        self.exam_id = exam_id
        self.vad_detector = VoiceActivityDetector()
        self.preprocessor = AudioPreprocessor()
        self.voice_detector = VoiceDetector()
        self.audio_buffer = AudioBuffer()
        self.event_manager = AudioEventManager()
        self.db_manager = MongoDBManager()

        # Statistics tracking
        self.vad_frames = 0
        self.total_frames = 0
        self.vad_scores = []
        self.background_speech_events = 0
        self.multiple_voices_events = 0

    def process_audio_chunk(
        self, audio_chunk: np.ndarray
    ) -> Dict[str, Any]:
        """
        Process an audio chunk through the complete pipeline.

        Args:
            audio_chunk: Audio data (16 kHz, mono, PCM 16-bit)

        Returns:
            Dictionary with analysis results
        """
        # Preprocess audio
        preprocessed = self.preprocessor.preprocess(audio_chunk)

        # Add to buffer
        self.audio_buffer.add_audio(preprocessed)

        # VAD detection
        vad_score = self.vad_detector.detect_voice_activity(preprocessed)
        self.vad_scores.append(vad_score)
        self.total_frames += 1

        if vad_score > 0.5:
            self.vad_frames += 1
            self.event_manager.create_vad_detected_event(vad_score)

        # Background speech detection
        background_detected, bg_confidence = self.voice_detector.detect_background_speech(
            preprocessed
        )
        if background_detected:
            self.background_speech_events += 1
            self.event_manager.create_background_speech_event(bg_confidence)

        # Multiple voices detection
        multiple_detected, speaker_count, multi_confidence = (
            self.voice_detector.detect_multiple_voices(preprocessed)
        )
        if multiple_detected:
            self.multiple_voices_events += 1
            self.event_manager.create_multiple_voices_event(speaker_count, multi_confidence)

        # Calculate current statistics
        current_stats = self._calculate_statistics()

        # Prepare result
        result = {
            "vad_score": float(vad_score),
            "background_speech_detected": background_detected,
            "background_speech_confidence": float(bg_confidence),
            "multiple_voices_detected": multiple_detected,
            "speaker_count": int(speaker_count),
            "multiple_voices_confidence": float(multi_confidence),
            "statistics": current_stats,
            "events": self.event_manager.get_events(),
        }

        return result

    def analyze_buffer(self) -> Dict[str, Any]:
        """
        Analyze the current audio buffer for detailed statistics.

        Returns:
            Dictionary with detailed analysis
        """
        buffer_audio = self.audio_buffer.get_buffer()

        if len(buffer_audio) == 0:
            return {
                "buffer_empty": True,
                "statistics": self._calculate_statistics(),
            }

        # Get speech timestamps
        speech_timestamps = self.vad_detector.get_speech_timestamps(buffer_audio)

        # Calculate speech/silence ratio
        speech_pct, silence_pct = self._calculate_speech_silence_ratio(speech_timestamps)

        # Create event
        window_s = self.audio_buffer.get_buffer_duration_s()
        self.event_manager.create_speech_silence_ratio_event(speech_pct, silence_pct, window_s)

        # Temporal analysis
        temporal_analysis = self.voice_detector.analyze_temporal_patterns(window_s)

        return {
            "buffer_duration_s": window_s,
            "speech_percentage": float(speech_pct),
            "silence_percentage": float(silence_pct),
            "speech_timestamps": speech_timestamps,
            "temporal_analysis": temporal_analysis,
            "statistics": self._calculate_statistics(),
        }

    def _calculate_statistics(self) -> Dict[str, Any]:
        """
        Calculate current statistics.

        Returns:
            Dictionary with statistics
        """
        avg_vad_score = float(np.mean(self.vad_scores)) if self.vad_scores else 0.0
        max_vad_score = float(np.max(self.vad_scores)) if self.vad_scores else 0.0
        min_vad_score = float(np.min(self.vad_scores)) if self.vad_scores else 0.0

        speech_pct = (
            (self.vad_frames / self.total_frames * 100)
            if self.total_frames > 0
            else 0.0
        )

        return {
            "total_frames": self.total_frames,
            "vad_frames": self.vad_frames,
            "speech_percentage": float(speech_pct),
            "avg_vad_score": avg_vad_score,
            "max_vad_score": max_vad_score,
            "min_vad_score": min_vad_score,
            "background_speech_events": self.background_speech_events,
            "multiple_voices_events": self.multiple_voices_events,
            "buffer_duration_s": self.audio_buffer.get_buffer_duration_s(),
        }

    def _calculate_speech_silence_ratio(
        self, speech_timestamps: List[Dict]
    ) -> Tuple[float, float]:
        """
        Calculate speech and silence percentages from timestamps.

        Args:
            speech_timestamps: List of speech timestamp ranges

        Returns:
            Tuple of (speech_pct, silence_pct)
        """
        if not speech_timestamps:
            return 0.0, 100.0

        buffer_duration_ms = self.audio_buffer.get_buffer_duration_s() * 1000

        total_speech_ms = 0
        for ts in speech_timestamps:
            total_speech_ms += ts["end"] - ts["start"]

        speech_pct = (total_speech_ms / buffer_duration_ms * 100) if buffer_duration_ms > 0 else 0.0
        silence_pct = 100.0 - speech_pct

        return float(speech_pct), float(silence_pct)

    def log_events_to_db(self) -> bool:
        """
        Log all events to MongoDB.

        Returns:
            True if successful
        """
        if not self.exam_id or not self.db_manager.is_connected():
            return False

        events = self.event_manager.get_events()
        for event in events:
            self.db_manager.insert_event(self.exam_id, event)

        return True

    def log_statistics_to_db(self) -> bool:
        """
        Log statistics to MongoDB.

        Returns:
            True if successful
        """
        if not self.exam_id or not self.db_manager.is_connected():
            return False

        stats = self._calculate_statistics()
        self.db_manager.insert_statistics(self.exam_id, stats)

        return True

    def get_events_from_db(self, event_type: str = None) -> List[Dict[str, Any]]:
        """
        Get events from MongoDB.

        Args:
            event_type: Optional event type filter

        Returns:
            List of events
        """
        if not self.exam_id:
            return []

        return self.db_manager.get_events(self.exam_id, event_type)

    def reset(self) -> None:
        """Reset pipeline for new analysis."""
        self.vad_frames = 0
        self.total_frames = 0
        self.vad_scores = []
        self.background_speech_events = 0
        self.multiple_voices_events = 0
        self.audio_buffer.clear()
        self.event_manager.clear_events()

    def shutdown(self) -> None:
        """Shutdown and cleanup pipeline."""
        self.db_manager.close()
