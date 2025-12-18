import pytest
import numpy as np
from src.audio_pipeline import AudioAnalysisPipeline
from src.config import SAMPLE_RATE, FRAME_SIZE


@pytest.fixture
def pipeline():
    """Create audio pipeline instance."""
    return AudioAnalysisPipeline(exam_id="test_exam_123")


class TestAudioAnalysisPipeline:
    """Tests for audio analysis pipeline."""

    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initializes correctly."""
        assert pipeline is not None
        assert pipeline.exam_id == "test_exam_123"
        assert pipeline.vad_detector is not None
        assert pipeline.preprocessor is not None
        assert pipeline.voice_detector is not None

    def test_process_silent_audio(self, pipeline):
        """Test processing silent audio."""
        silent_audio = np.zeros(FRAME_SIZE, dtype=np.float32)

        result = pipeline.process_audio_chunk(silent_audio)

        assert "vad_score" in result
        assert "background_speech_detected" in result
        assert "multiple_voices_detected" in result
        assert "statistics" in result

        # VAD score should be low for silent audio
        assert result["vad_score"] < 0.5

    def test_process_noise_audio(self, pipeline):
        """Test processing noise audio."""
        noise_audio = np.random.randn(FRAME_SIZE).astype(np.float32) * 0.1

        result = pipeline.process_audio_chunk(noise_audio)

        assert "vad_score" in result
        assert 0.0 <= result["vad_score"] <= 1.0

    def test_process_multiple_chunks(self, pipeline):
        """Test processing multiple audio chunks."""
        for i in range(5):
            audio = np.random.randn(FRAME_SIZE).astype(np.float32) * 0.1
            result = pipeline.process_audio_chunk(audio)

            assert result is not None
            assert result["vad_score"] is not None

        # Check statistics are being accumulated
        stats = pipeline._calculate_statistics()
        assert stats["total_frames"] == 5

    def test_statistics_calculation(self, pipeline):
        """Test statistics calculation."""
        # Process some audio
        for _ in range(10):
            audio = np.random.randn(FRAME_SIZE).astype(np.float32) * 0.05
            pipeline.process_audio_chunk(audio)

        stats = pipeline._calculate_statistics()

        assert "total_frames" in stats
        assert "vad_frames" in stats
        assert "speech_percentage" in stats
        assert "avg_vad_score" in stats
        assert "max_vad_score" in stats
        assert "min_vad_score" in stats

        assert stats["total_frames"] == 10
        assert 0.0 <= stats["speech_percentage"] <= 100.0
        assert 0.0 <= stats["avg_vad_score"] <= 1.0

    def test_buffer_analysis(self, pipeline):
        """Test buffer analysis."""
        # Fill buffer with audio
        for _ in range(20):
            audio = np.random.randn(FRAME_SIZE).astype(np.float32) * 0.05
            pipeline.process_audio_chunk(audio)

        result = pipeline.analyze_buffer()

        assert "buffer_duration_s" in result
        assert "speech_percentage" in result
        assert "silence_percentage" in result
        assert "speech_timestamps" in result

        # Speech + silence should equal 100%
        assert abs(
            result["speech_percentage"] + result["silence_percentage"] - 100.0
        ) < 0.1

    def test_pipeline_reset(self, pipeline):
        """Test pipeline reset."""
        # Add some data
        for _ in range(5):
            audio = np.random.randn(FRAME_SIZE).astype(np.float32) * 0.05
            pipeline.process_audio_chunk(audio)

        # Verify data is there
        assert pipeline.total_frames == 5

        # Reset
        pipeline.reset()

        # Verify reset
        assert pipeline.total_frames == 0
        assert pipeline.vad_frames == 0
        assert len(pipeline.vad_scores) == 0

    def test_event_generation(self, pipeline):
        """Test event generation during processing."""
        # Process synthetic speech
        t = np.arange(FRAME_SIZE) / SAMPLE_RATE
        speech = np.sin(2 * np.pi * 500 * t).astype(np.float32)

        result = pipeline.process_audio_chunk(speech)

        assert "events" in result
        assert isinstance(result["events"], list)

    def test_pipeline_without_exam_id(self):
        """Test pipeline without exam ID."""
        pipeline = AudioAnalysisPipeline()

        audio = np.random.randn(FRAME_SIZE).astype(np.float32) * 0.05
        result = pipeline.process_audio_chunk(audio)

        assert result is not None
        # Database logging should not occur without exam ID
        # but processing should continue


class TestAudioEventGeneration:
    """Tests for audio event generation."""

    def test_vad_event_on_speech(self):
        """Test VAD event generation on speech."""
        pipeline = AudioAnalysisPipeline()

        # Create synthetic speech
        t = np.arange(FRAME_SIZE) / SAMPLE_RATE
        speech = np.sin(2 * np.pi * 500 * t).astype(np.float32)

        result = pipeline.process_audio_chunk(speech)

        assert len(result["events"]) > 0

    def test_background_speech_event(self):
        """Test background speech event generation."""
        pipeline = AudioAnalysisPipeline()

        # Process multiple chunks with varying energy
        for _ in range(3):
            audio = np.random.randn(FRAME_SIZE).astype(np.float32) * 0.15
            pipeline.process_audio_chunk(audio)


class TestSpeechSilenceRatio:
    """Tests for speech/silence ratio calculation."""

    def test_speech_silence_ratio_all_silence(self):
        """Test ratio with all silence."""
        pipeline = AudioAnalysisPipeline()

        # Process silent audio
        for _ in range(10):
            silent = np.zeros(FRAME_SIZE, dtype=np.float32)
            pipeline.process_audio_chunk(silent)

        result = pipeline.analyze_buffer()

        # Should be mostly silence
        assert result["silence_percentage"] > 90.0

    def test_speech_silence_ratio_mixed(self):
        """Test ratio with mixed speech and silence."""
        pipeline = AudioAnalysisPipeline()

        # Alternate between speech and silence
        for i in range(20):
            if i % 2 == 0:
                t = np.arange(FRAME_SIZE) / SAMPLE_RATE
                audio = np.sin(2 * np.pi * 500 * t).astype(np.float32)
            else:
                audio = np.zeros(FRAME_SIZE, dtype=np.float32)

            pipeline.process_audio_chunk(audio)

        result = pipeline.analyze_buffer()

        # Should have reasonable split
        assert 0.0 < result["speech_percentage"] < 100.0
        assert 0.0 < result["silence_percentage"] < 100.0
