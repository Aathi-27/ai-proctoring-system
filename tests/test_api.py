import pytest
import numpy as np
import io
import base64
from scipy.io.wavfile import write
from src.api import app
from src.config import SAMPLE_RATE


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_audio():
    """Create sample audio data (WAV format)."""
    # Create 1 second of 500 Hz sine wave
    duration = 1.0
    samples = int(SAMPLE_RATE * duration)
    t = np.arange(samples) / SAMPLE_RATE
    audio = np.sin(2 * np.pi * 500 * t) * 0.5

    # Convert to 16-bit PCM
    audio = (audio * 32767).astype(np.int16)

    # Write to WAV format
    wav_buffer = io.BytesIO()
    write(wav_buffer, SAMPLE_RATE, audio)
    wav_buffer.seek(0)

    return wav_buffer.getvalue()


@pytest.fixture
def sample_audio_base64(sample_audio):
    """Create base64 encoded sample audio."""
    return base64.b64encode(sample_audio).decode("utf-8")


class TestHealthEndpoint:
    """Tests for health endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"


class TestAudioAnalysisEndpoint:
    """Tests for audio analysis endpoint."""

    def test_analyze_audio_wav(self, client, sample_audio):
        """Test analyzing audio with WAV format."""
        response = client.post(
            "/exams/test_exam_001/analyze-audio",
            data=sample_audio,
            content_type="audio/wav",
        )

        assert response.status_code == 200
        data = response.get_json()

        assert "vad_score" in data
        assert "background_speech_detected" in data
        assert "multiple_voices_detected" in data
        assert "speaker_count" in data
        assert 0.0 <= data["vad_score"] <= 1.0

    def test_analyze_audio_json_base64(self, client, sample_audio_base64):
        """Test analyzing audio with JSON base64 encoding."""
        response = client.post(
            "/exams/test_exam_002/analyze-audio",
            json={"audio_base64": sample_audio_base64},
        )

        assert response.status_code == 200
        data = response.get_json()

        assert "vad_score" in data
        assert "background_speech_detected" in data

    def test_analyze_audio_invalid_format(self, client):
        """Test analyzing with invalid audio format."""
        response = client.post(
            "/exams/test_exam_003/analyze-audio",
            data=b"invalid audio data",
            content_type="audio/wav",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_analyze_audio_missing_data(self, client):
        """Test analyzing without audio data."""
        response = client.post("/exams/test_exam_004/analyze-audio")

        assert response.status_code == 400


class TestBufferAnalysisEndpoint:
    """Tests for buffer analysis endpoint."""

    def test_analyze_buffer_empty(self, client):
        """Test analyzing empty buffer."""
        response = client.get("/exams/test_exam_005/analyze-buffer")

        assert response.status_code == 200
        data = response.get_json()

        assert "buffer_duration_s" in data

    def test_analyze_buffer_with_data(self, client, sample_audio):
        """Test buffer analysis with data."""
        # First add audio
        client.post(
            "/exams/test_exam_006/analyze-audio",
            data=sample_audio,
            content_type="audio/wav",
        )

        # Then analyze buffer
        response = client.get("/exams/test_exam_006/analyze-buffer")

        assert response.status_code == 200
        data = response.get_json()

        assert "buffer_duration_s" in data
        assert "speech_percentage" in data
        assert "silence_percentage" in data


class TestStatisticsEndpoint:
    """Tests for statistics endpoint."""

    def test_get_statistics(self, client, sample_audio):
        """Test getting statistics."""
        # Add audio first
        client.post(
            "/exams/test_exam_007/analyze-audio",
            data=sample_audio,
            content_type="audio/wav",
        )

        response = client.get("/exams/test_exam_007/statistics")

        assert response.status_code == 200
        data = response.get_json()

        assert "statistics" in data
        stats = data["statistics"]

        assert "total_frames" in stats
        assert "vad_frames" in stats
        assert "speech_percentage" in stats


class TestEventsEndpoint:
    """Tests for events endpoint."""

    def test_get_events(self, client, sample_audio):
        """Test getting events."""
        # Add audio first
        client.post(
            "/exams/test_exam_008/analyze-audio",
            data=sample_audio,
            content_type="audio/wav",
        )

        response = client.get("/exams/test_exam_008/events")

        assert response.status_code == 200
        data = response.get_json()

        assert "events" in data
        assert "count" in data
        assert isinstance(data["events"], list)

    def test_get_events_with_filter(self, client, sample_audio):
        """Test getting events with type filter."""
        # Add audio first
        client.post(
            "/exams/test_exam_009/analyze-audio",
            data=sample_audio,
            content_type="audio/wav",
        )

        # Query with event type filter
        response = client.get(
            "/exams/test_exam_009/events",
            query_string={"event_type": "VAD_DETECTED"},
        )

        assert response.status_code == 200
        data = response.get_json()

        assert "event_type_filter" in data
        assert data["event_type_filter"] == "VAD_DETECTED"

    def test_get_events_with_limit(self, client, sample_audio):
        """Test getting events with limit."""
        # Add audio multiple times
        for _ in range(5):
            client.post(
                "/exams/test_exam_010/analyze-audio",
                data=sample_audio,
                content_type="audio/wav",
            )

        response = client.get(
            "/exams/test_exam_010/events",
            query_string={"limit": 2},
        )

        assert response.status_code == 200
        data = response.get_json()

        # Should return at most 2 events
        assert len(data["events"]) <= 2


class TestResetEndpoint:
    """Tests for reset endpoint."""

    def test_reset_analysis(self, client, sample_audio):
        """Test resetting analysis."""
        # Add audio
        client.post(
            "/exams/test_exam_011/analyze-audio",
            data=sample_audio,
            content_type="audio/wav",
        )

        # Reset
        response = client.post("/exams/test_exam_011/reset")

        assert response.status_code == 200
        data = response.get_json()

        assert data["status"] == "reset"


class TestShutdownEndpoint:
    """Tests for shutdown endpoint."""

    def test_shutdown_analysis(self, client, sample_audio):
        """Test shutting down analysis."""
        # Add audio
        client.post(
            "/exams/test_exam_012/analyze-audio",
            data=sample_audio,
            content_type="audio/wav",
        )

        # Shutdown
        response = client.post("/exams/test_exam_012/shutdown")

        assert response.status_code == 200
        data = response.get_json()

        assert data["status"] == "shutdown"
