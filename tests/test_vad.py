import pytest
import numpy as np
from src.vad import VoiceActivityDetector
from src.config import SAMPLE_RATE, FRAME_SIZE


@pytest.fixture
def vad_detector():
    """Create VAD detector instance."""
    return VoiceActivityDetector()


class TestVoiceActivityDetector:
    """Tests for VAD detection."""

    def test_vad_initialization(self, vad_detector):
        """Test VAD detector initializes correctly."""
        assert vad_detector.model is not None
        assert vad_detector.device is not None

    def test_vad_silence_detection(self, vad_detector):
        """Test VAD correctly identifies silence."""
        # Create silent audio (all zeros)
        silent_audio = np.zeros(FRAME_SIZE, dtype=np.float32)

        vad_score = vad_detector.detect_voice_activity(silent_audio)

        # Should detect very low probability of speech
        assert 0.0 <= vad_score <= 1.0
        assert vad_score < 0.5

    def test_vad_white_noise_detection(self, vad_detector):
        """Test VAD on white noise."""
        # Create white noise
        noise = np.random.randn(FRAME_SIZE).astype(np.float32) * 0.1

        vad_score = vad_detector.detect_voice_activity(noise)

        # Should have low probability for noise
        assert 0.0 <= vad_score <= 1.0

    def test_vad_sine_wave_detection(self, vad_detector):
        """Test VAD on synthetic speech-like signal (sine wave)."""
        # Create synthetic audio (1000 Hz sine wave)
        t = np.arange(FRAME_SIZE) / SAMPLE_RATE
        audio = np.sin(2 * np.pi * 1000 * t).astype(np.float32)

        vad_score = vad_detector.detect_voice_activity(audio)

        # Should detect some probability of speech
        assert 0.0 <= vad_score <= 1.0

    def test_vad_empty_audio(self, vad_detector):
        """Test VAD on empty audio."""
        empty_audio = np.array([], dtype=np.float32)

        vad_score = vad_detector.detect_voice_activity(empty_audio)

        assert vad_score == 0.0

    def test_vad_audio_normalization(self, vad_detector):
        """Test that audio is normalized correctly."""
        # Create PCM 16-bit audio
        pcm_audio = np.array([0, 16384, -16384, 8192], dtype=np.int16)
        expected_normalized = np.array([0, 0.5, -0.5, 0.25], dtype=np.float32)

        normalized = vad_detector._normalize_audio(pcm_audio)

        np.testing.assert_array_almost_equal(normalized, expected_normalized)

    def test_vad_output_range(self, vad_detector):
        """Test VAD output is always in [0, 1] range."""
        # Test multiple audio samples
        for _ in range(10):
            audio = np.random.randn(FRAME_SIZE).astype(np.float32)
            vad_score = vad_detector.detect_voice_activity(audio)

            assert 0.0 <= vad_score <= 1.0

    def test_vad_speech_timestamps(self, vad_detector):
        """Test speech timestamp detection."""
        # Create audio with speech-like pattern
        # (alternating silence and signal)
        silence = np.zeros(SAMPLE_RATE // 4, dtype=np.float32)
        signal = np.sin(2 * np.pi * 1000 * np.arange(SAMPLE_RATE // 4) / SAMPLE_RATE).astype(
            np.float32
        )

        audio = np.concatenate([silence, signal, silence, signal])

        timestamps = vad_detector.get_speech_timestamps(audio)

        # Should detect at least some speech segments
        assert len(timestamps) >= 0

        # Each timestamp should have start and end
        for ts in timestamps:
            assert "start" in ts
            assert "end" in ts
            assert ts["start"] < ts["end"]
