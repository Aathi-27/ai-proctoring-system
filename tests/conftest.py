"""
Pytest configuration and shared fixtures.
"""

import pytest
import numpy as np
import io
from scipy.io.wavfile import write
from src.config import SAMPLE_RATE


@pytest.fixture(scope="session")
def audio_sample_mono_speech():
    """Create a mono speech-like audio sample (500 Hz sine wave)."""
    duration = 1.0
    samples = int(SAMPLE_RATE * duration)
    t = np.arange(samples) / SAMPLE_RATE
    audio = np.sin(2 * np.pi * 500 * t).astype(np.float32) * 0.5
    return audio


@pytest.fixture(scope="session")
def audio_sample_silence():
    """Create a silent audio sample."""
    samples = int(SAMPLE_RATE * 1.0)
    return np.zeros(samples, dtype=np.float32)


@pytest.fixture(scope="session")
def audio_sample_noise():
    """Create a noise audio sample."""
    samples = int(SAMPLE_RATE * 1.0)
    return np.random.randn(samples).astype(np.float32) * 0.1


@pytest.fixture(scope="session")
def audio_sample_wav():
    """Create a WAV file as bytes."""
    duration = 1.0
    samples = int(SAMPLE_RATE * duration)
    t = np.arange(samples) / SAMPLE_RATE
    audio = np.sin(2 * np.pi * 500 * t) * 0.5
    audio = (audio * 32767).astype(np.int16)

    wav_buffer = io.BytesIO()
    write(wav_buffer, SAMPLE_RATE, audio)
    wav_buffer.seek(0)

    return wav_buffer.getvalue()


@pytest.fixture
def temp_exam_id():
    """Generate a temporary exam ID."""
    import uuid
    return f"test_exam_{uuid.uuid4().hex[:8]}"
