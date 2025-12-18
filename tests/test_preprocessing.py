import pytest
import numpy as np
from src.preprocessing import AudioPreprocessor
from src.config import SAMPLE_RATE


@pytest.fixture
def preprocessor():
    """Create preprocessor instance."""
    return AudioPreprocessor()


class TestAudioPreprocessor:
    """Tests for audio preprocessing."""

    def test_preprocessor_initialization(self, preprocessor):
        """Test preprocessor initializes correctly."""
        assert preprocessor is not None

    def test_preprocess_basic(self, preprocessor):
        """Test basic preprocessing pipeline."""
        audio = np.random.randn(SAMPLE_RATE // 2).astype(np.float32)

        processed = preprocessor.preprocess(audio)

        assert processed.shape == audio.shape
        assert processed.dtype == np.float32

    def test_normalize_audio(self, preprocessor):
        """Test audio normalization."""
        # Create audio with peak amplitude of 2.0
        audio = np.array([0, 1, -1, 0.5, -2], dtype=np.float32)

        normalized = preprocessor._normalize(audio)

        # After normalization, max should be 1.0 or close to it
        assert np.max(np.abs(normalized)) <= 1.0
        # Values should be proportional
        assert normalized[2] < normalized[1]

    def test_normalize_silent_audio(self, preprocessor):
        """Test normalization of silent audio."""
        silent_audio = np.zeros(100, dtype=np.float32)

        normalized = preprocessor._normalize(silent_audio)

        # Should remain silent
        np.testing.assert_array_equal(normalized, silent_audio)

    def test_noise_reduction(self, preprocessor):
        """Test noise reduction."""
        # Create audio with low-frequency noise
        noise = np.sin(2 * np.pi * 50 * np.arange(SAMPLE_RATE) / SAMPLE_RATE).astype(np.float32)

        filtered = preprocessor._reduce_noise(noise)

        assert filtered.shape == noise.shape
        # High-pass filter should reduce low frequencies
        assert np.abs(filtered).mean() < np.abs(noise).mean()

    def test_rms_energy(self, preprocessor):
        """Test RMS energy calculation."""
        # Create audio with known RMS
        audio = np.ones(1000, dtype=np.float32)

        rms = preprocessor.get_rms_energy(audio)

        assert rms == 1.0

    def test_rms_energy_silent(self, preprocessor):
        """Test RMS energy of silent audio."""
        silent_audio = np.zeros(100, dtype=np.float32)

        rms = preprocessor.get_rms_energy(silent_audio)

        assert rms == 0.0

    def test_audio_to_db(self, preprocessor):
        """Test amplitude to dB conversion."""
        # 1.0 amplitude = 0 dB
        db = preprocessor.audio_to_db(1.0)
        assert db == 0.0

        # 0.5 amplitude should be negative dB
        db_half = preprocessor.audio_to_db(0.5)
        assert db_half < 0.0

        # Larger amplitude should be positive dB
        db_double = preprocessor.audio_to_db(2.0)
        assert db_double > 0.0

    def test_audio_to_db_zero(self, preprocessor):
        """Test dB conversion for zero amplitude."""
        db = preprocessor.audio_to_db(0.0)
        assert np.isinf(db) and db == -np.inf

    def test_mfcc_features(self, preprocessor):
        """Test MFCC extraction."""
        audio = np.random.randn(SAMPLE_RATE // 2).astype(np.float32)

        mfcc = preprocessor.extract_mfcc_features(audio, n_mfcc=13)

        assert mfcc.shape[0] == 13
        assert mfcc.shape[1] > 0

    def test_spectral_features(self, preprocessor):
        """Test spectral feature extraction."""
        audio = np.random.randn(SAMPLE_RATE // 2).astype(np.float32)

        features = preprocessor.extract_spectral_features(audio)

        assert "spectral_centroid" in features
        assert "spectral_rolloff" in features
        assert "spectral_energy" in features
        assert "zero_crossing_rate" in features

        # Check ranges
        assert 0 <= features["spectral_centroid"] <= SAMPLE_RATE / 2
        assert 0 <= features["spectral_energy"]
        assert 0 <= features["zero_crossing_rate"]
