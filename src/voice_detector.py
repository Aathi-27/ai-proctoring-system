import numpy as np
from typing import Dict, List, Tuple
from collections import deque
from src.config import (
    SAMPLE_RATE,
    BACKGROUND_SPEECH_THRESHOLD,
    MULTIPLE_VOICES_THRESHOLD,
    VOICE_DETECTION_WINDOW_MS,
    FRAME_DURATION_MS,
)
from src.preprocessing import AudioPreprocessor


class VoiceDetector:
    """
    Detects background speech and multiple voices using spectral features.
    """

    def __init__(self):
        """Initialize the voice detector."""
        self.preprocessor = AudioPreprocessor()
        self.voice_history = deque(
            maxlen=int(VOICE_DETECTION_WINDOW_MS / FRAME_DURATION_MS)
        )
        self.speaker_energy_history = deque(
            maxlen=int(VOICE_DETECTION_WINDOW_MS / FRAME_DURATION_MS)
        )

    def detect_background_speech(
        self, audio_chunk: np.ndarray, candidate_voice_profile: Dict = None
    ) -> Tuple[bool, float]:
        """
        Detect background speech (non-candidate voices).

        Args:
            audio_chunk: Audio data
            candidate_voice_profile: Acoustic profile of candidate's voice (optional)

        Returns:
            Tuple of (background_speech_detected, confidence_score)
        """
        # Extract spectral features
        features = self.preprocessor.extract_spectral_features(audio_chunk)

        # Get energy level
        energy = self.preprocessor.get_rms_energy(audio_chunk)

        # Calculate confidence based on features
        confidence = self._calculate_background_speech_confidence(features, energy)

        detected = confidence > BACKGROUND_SPEECH_THRESHOLD

        return detected, confidence

    def detect_multiple_voices(self, audio_chunk: np.ndarray) -> Tuple[bool, int, float]:
        """
        Detect multiple speakers using energy-based estimation.

        Args:
            audio_chunk: Audio data

        Returns:
            Tuple of (multiple_voices_detected, speaker_count, confidence)
        """
        # Extract spectral features
        features = self.preprocessor.extract_spectral_features(audio_chunk)

        # Get energy
        energy = self.preprocessor.get_rms_energy(audio_chunk)

        # Update history
        self.speaker_energy_history.append(energy)

        # Estimate speaker count
        speaker_count = self._estimate_speaker_count(features, energy)

        # Calculate confidence
        confidence = self._calculate_multiple_voices_confidence(features, speaker_count)

        # Multiple voices detected if speaker_count >= 2
        detected = speaker_count >= 2

        return detected, speaker_count, confidence

    def _calculate_background_speech_confidence(
        self, features: Dict, energy: float
    ) -> float:
        """
        Calculate confidence score for background speech detection.

        Args:
            features: Spectral features
            energy: RMS energy

        Returns:
            Confidence score (0-1)
        """
        # Normalize features to [0, 1]
        centroid_norm = min(features["spectral_centroid"] / 8000, 1.0)
        rolloff_norm = min(features["spectral_rolloff"] / 16000, 1.0)

        # Higher energy and varied spectrum suggests speech
        energy_factor = min(energy / 0.1, 1.0)  # Normalize to typical speech energy
        spectral_variance = abs(rolloff_norm - centroid_norm)

        # Combine factors
        confidence = (energy_factor * 0.5 + spectral_variance * 0.5)
        confidence = min(confidence, 1.0)

        return confidence

    def _estimate_speaker_count(self, features: Dict, energy: float) -> int:
        """
        Estimate number of speakers using energy distribution.

        Args:
            features: Spectral features
            energy: RMS energy

        Returns:
            Estimated speaker count
        """
        # Single speaker baseline
        speaker_count = 1

        # High energy and high spectral variance suggest multiple speakers
        if len(self.speaker_energy_history) > 1:
            energy_std = float(np.std(list(self.speaker_energy_history)))
            energy_mean = float(np.mean(list(self.speaker_energy_history)))

            # If standard deviation is high, energy is varying (multiple speakers)
            if energy_mean > 0.01 and energy_std / energy_mean > 0.3:
                speaker_count = 2

            # Very high variance suggests more voices
            if energy_mean > 0.01 and energy_std / energy_mean > 0.6:
                speaker_count = 3

        # Use spectral centroid spread as additional indicator
        centroid_variation = features["spectral_centroid"]
        if centroid_variation > 4000:
            speaker_count = max(speaker_count, 2)

        return min(speaker_count, 4)  # Cap at 4 speakers

    def _calculate_multiple_voices_confidence(
        self, features: Dict, speaker_count: int
    ) -> float:
        """
        Calculate confidence score for multiple voices detection.

        Args:
            features: Spectral features
            speaker_count: Estimated speaker count

        Returns:
            Confidence score (0-1)
        """
        # Base confidence on speaker count
        if speaker_count < 2:
            return 0.0

        # Higher speaker count = higher confidence
        confidence = min((speaker_count - 1) / 3, 1.0)

        # Adjust based on spectral characteristics
        spectral_variation = abs(
            features["spectral_rolloff"] - features["spectral_centroid"]
        )
        spectral_norm = min(spectral_variation / 8000, 1.0)

        # Combine
        confidence = (confidence * 0.6 + spectral_norm * 0.4)

        return min(confidence, 1.0)

    def analyze_temporal_patterns(self, window_duration_s: float = 5.0) -> Dict:
        """
        Analyze temporal patterns of voice activity over a time window.

        Args:
            window_duration_s: Duration of analysis window in seconds

        Returns:
            Dictionary with temporal analysis
        """
        if len(self.speaker_energy_history) == 0:
            return {
                "has_multiple_voices": False,
                "confidence": 0.0,
                "duration_s": 0.0,
                "voice_transitions": 0,
            }

        energies = list(self.speaker_energy_history)
        energy_array = np.array(energies)

        # Calculate statistics
        mean_energy = float(np.mean(energy_array))
        std_energy = float(np.std(energy_array))
        energy_range = float(np.max(energy_array) - np.min(energy_array))

        # Count transitions (changes in energy distribution)
        transitions = 0
        for i in range(1, len(energies)):
            if abs(energies[i] - energies[i - 1]) > std_energy * 0.5:
                transitions += 1

        # Multiple voices indicated by high variance and transitions
        has_multiple = std_energy > mean_energy * 0.2 and transitions > 2

        duration_s = len(self.speaker_energy_history) * FRAME_DURATION_MS / 1000.0

        return {
            "has_multiple_voices": has_multiple,
            "confidence": min((transitions / 10.0) * (std_energy / (mean_energy + 1e-6)), 1.0),
            "duration_s": duration_s,
            "voice_transitions": transitions,
        }
