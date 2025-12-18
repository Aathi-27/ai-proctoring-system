import pytest
import numpy as np
from src.voice_detector import VoiceDetector
from src.config import SAMPLE_RATE


@pytest.fixture
def voice_detector():
    """Create voice detector instance."""
    return VoiceDetector()


class TestVoiceDetector:
    """Tests for voice detection."""

    def test_voice_detector_initialization(self, voice_detector):
        """Test voice detector initializes correctly."""
        assert voice_detector is not None
        assert voice_detector.preprocessor is not None

    def test_background_speech_detection_silent(self, voice_detector):
        """Test background speech detection on silent audio."""
        silent_audio = np.zeros(SAMPLE_RATE // 2, dtype=np.float32)

        detected, confidence = voice_detector.detect_background_speech(silent_audio)

        assert isinstance(detected, (bool, np.bool_))
        assert 0.0 <= confidence <= 1.0

    def test_background_speech_detection_noisy(self, voice_detector):
        """Test background speech detection on noisy audio."""
        # Create random audio (simulates speech)
        noise = np.random.randn(SAMPLE_RATE // 2).astype(np.float32) * 0.1

        detected, confidence = voice_detector.detect_background_speech(noise)

        assert isinstance(detected, (bool, np.bool_))
        assert 0.0 <= confidence <= 1.0

    def test_multiple_voices_detection_single(self, voice_detector):
        """Test multiple voices detection with single voice."""
        audio = np.random.randn(SAMPLE_RATE // 2).astype(np.float32) * 0.05

        detected, speaker_count, confidence = voice_detector.detect_multiple_voices(audio)

        assert isinstance(detected, (bool, np.bool_))
        assert isinstance(speaker_count, (int, np.integer))
        assert 0.0 <= confidence <= 1.0
        assert speaker_count >= 1

    def test_multiple_voices_detection_multiple(self, voice_detector):
        """Test multiple voices detection with varying energy."""
        # Create audio with varying energy (simulates multiple speakers)
        audio = np.random.randn(SAMPLE_RATE // 2).astype(np.float32)

        # Process multiple chunks to build history
        for _ in range(10):
            voice_detector.detect_multiple_voices(audio)

        detected, speaker_count, confidence = voice_detector.detect_multiple_voices(audio)

        assert isinstance(detected, (bool, np.bool_))
        assert isinstance(speaker_count, (int, np.integer))
        assert 0.0 <= confidence <= 1.0

    def test_temporal_patterns_analysis(self, voice_detector):
        """Test temporal pattern analysis."""
        # Build up history
        for i in range(20):
            # Alternate energy levels
            energy_level = 0.05 if i % 2 == 0 else 0.1
            audio = np.random.randn(SAMPLE_RATE // 16).astype(np.float32) * energy_level
            voice_detector.detect_multiple_voices(audio)

        result = voice_detector.analyze_temporal_patterns()

        assert "has_multiple_voices" in result
        assert "confidence" in result
        assert "duration_s" in result
        assert "voice_transitions" in result

        assert isinstance(result["has_multiple_voices"], (bool, np.bool_))
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["duration_s"] >= 0.0
        assert result["voice_transitions"] >= 0

    def test_background_speech_confidence_calculation(self, voice_detector):
        """Test background speech confidence calculation."""
        # Create audio with speech-like characteristics
        t = np.arange(SAMPLE_RATE // 4) / SAMPLE_RATE
        audio = np.sin(2 * np.pi * 500 * t).astype(np.float32)

        features = voice_detector.preprocessor.extract_spectral_features(audio)
        energy = voice_detector.preprocessor.get_rms_energy(audio)

        confidence = voice_detector._calculate_background_speech_confidence(features, energy)

        assert 0.0 <= confidence <= 1.0

    def test_multiple_voices_confidence_calculation(self, voice_detector):
        """Test multiple voices confidence calculation."""
        # Create audio with varied spectrum
        t = np.arange(SAMPLE_RATE // 4) / SAMPLE_RATE
        audio = (
            np.sin(2 * np.pi * 500 * t) + np.sin(2 * np.pi * 1000 * t)
        ).astype(np.float32) / 2

        features = voice_detector.preprocessor.extract_spectral_features(audio)
        speaker_count = 2

        confidence = voice_detector._calculate_multiple_voices_confidence(features, speaker_count)

        assert 0.0 <= confidence <= 1.0

    def test_speaker_count_estimation(self, voice_detector):
        """Test speaker count estimation."""
        t = np.arange(SAMPLE_RATE // 4) / SAMPLE_RATE
        audio = np.sin(2 * np.pi * 500 * t).astype(np.float32)

        features = voice_detector.preprocessor.extract_spectral_features(audio)
        energy = voice_detector.preprocessor.get_rms_energy(audio)

        speaker_count = voice_detector._estimate_speaker_count(features, energy)

        assert 1 <= speaker_count <= 4
